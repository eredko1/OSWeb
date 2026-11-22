'use strict';
// OSWeb web proxy core. Fetches a page on behalf of the OSWeb Safari app and strips the headers that forbid
// embedding it in a frame. Designed to be safe to expose: it only serves requests signed with PROXY_SECRET
// (HMAC over url + expiry), refuses private/loopback addresses (SSRF), follows redirects manually and
// re-checks every hop, forwards no cookies, and caps size and time.
const crypto = require('crypto');
const dns = require('dns').promises;
const net = require('net');

const MAX_BYTES = 10 * 1024 * 1024;
const TIMEOUT_MS = 15000;
const UA = 'Mozilla/5.0 (OSWeb proxy) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15';

function isPrivateIp(ip) {
  if (net.isIPv4(ip)) {
    const [a, b] = ip.split('.').map(Number);
    return a === 10 || a === 127 || a === 0 || (a === 169 && b === 254) || (a === 172 && b >= 16 && b <= 31) || (a === 192 && b === 168) || (a === 100 && b >= 64 && b <= 127) || a >= 224;
  }
  const v = ip.toLowerCase();
  return v === '::1' || v === '::' || v.startsWith('fc') || v.startsWith('fd') || v.startsWith('fe80') || v.startsWith('::ffff:127.') || v.startsWith('::ffff:10.') || v.startsWith('::ffff:192.168.');
}

function sign(secret, url, exp) { return crypto.createHmac('sha256', secret).update(`${url}|${exp}`).digest('hex'); }
function verify(secret, url, exp, sig) {
  if (!secret || !url || !exp || !sig) return false;
  if (!/^\d{10,16}$/.test(String(exp)) || Number(exp) < Date.now() || Number(exp) > Date.now() + 3600e3) return false;
  const want = Buffer.from(sign(secret, url, exp)); const got = Buffer.from(String(sig));
  return want.length === got.length && crypto.timingSafeEqual(want, got);
}

async function assertPublicHost(hostname, allowPrivate) {
  if (allowPrivate) return;
  const addrs = net.isIP(hostname) ? [{ address: hostname }] : await dns.lookup(hostname, { all: true });
  if (!addrs.length || addrs.some(a => isPrivateIp(a.address))) { const e = new Error('Blocked address'); e.status = 403; throw e; }
}

async function fetchFollow(target, allowPrivate, hops = 0) {
  const u = new URL(target);
  if (u.protocol !== 'http:' && u.protocol !== 'https:') { const e = new Error('Only http(s) URLs'); e.status = 400; throw e; }
  await assertPublicHost(u.hostname, allowPrivate);
  const res = await fetch(u, { redirect: 'manual', headers: { 'user-agent': UA, accept: 'text/html,application/xhtml+xml,*/*;q=0.8', 'accept-language': 'en-US,en;q=0.9' }, signal: AbortSignal.timeout(TIMEOUT_MS) });
  const loc = res.headers.get('location');
  if (res.status >= 300 && res.status < 400 && loc) { if (hops >= 5) { const e = new Error('Too many redirects'); e.status = 508; throw e; } return fetchFollow(new URL(loc, u).href, allowPrivate, hops + 1); }
  return { res, url: u };
}

const INJECT = `<script>(function(){function send(u){try{parent.postMessage({type:'osweb-nav',url:u},'*')}catch(e){}}
document.addEventListener('click',function(e){var a=e.target&&e.target.closest&&e.target.closest('a[href]');if(!a)return;var h=a.href;if(!/^https?:/i.test(h))return;e.preventDefault();send(h)},true);
document.addEventListener('submit',function(e){var f=e.target;if(((f.method||'get')+'').toLowerCase()!=='get')return;e.preventDefault();var u=new URL(f.action||document.baseURI);new FormData(f).forEach(function(v,k){if(typeof v==='string')u.searchParams.set(k,v)});send(u.href)},true);
var o=window.open;window.open=function(u){if(u)send(new URL(u,document.baseURI).href);return null};})();</script>`;

function rewriteHtml(html, baseUrl) {
  let out = html.replace(/<meta[^>]+http-equiv=["']?(content-security-policy|x-frame-options|refresh)["']?[^>]*>/gi, '');
  const head = `<base href="${baseUrl.replace(/"/g, '&quot;')}">${INJECT}`;
  if (/<head[^>]*>/i.test(out)) return out.replace(/<head[^>]*>/i, m => m + head);
  return head + out;
}

// Node (req, res) handler shared by Vercel (api/p.js) and the standalone server.
async function handle(req, res, opts = {}) {
  const secret = opts.secret || process.env.PROXY_SECRET;
  const allowPrivate = opts.allowPrivate || process.env.ALLOW_PRIVATE === '1';
  const origin = (req.headers['origin'] || '*');
  const send = (status, body, headers = {}) => { res.statusCode = status; Object.entries({ 'x-robots-tag': 'noindex', 'referrer-policy': 'no-referrer', ...headers }).forEach(([k, v]) => res.setHeader(k, v)); res.end(body); };
  try {
    const q = new URL(req.url, 'http://x').searchParams;
    if (q.get('health') === '1') return send(200, JSON.stringify({ ok: true, signed: !!secret }), { 'content-type': 'application/json', 'access-control-allow-origin': origin });
    if (!secret) return send(503, 'Proxy is not configured: set PROXY_SECRET.');
    if (req.method !== 'GET') return send(405, 'GET only');
    const target = q.get('url');
    if (!verify(secret, target, q.get('exp'), q.get('sig'))) return send(403, 'Bad or expired signature');
    const { res: up, url } = await fetchFollow(target, allowPrivate);
    const type = up.headers.get('content-type') || 'application/octet-stream';
    const len = Number(up.headers.get('content-length') || 0);
    if (len > MAX_BYTES) return send(413, 'Too large');
    const buf = Buffer.from(await up.arrayBuffer());
    if (buf.length > MAX_BYTES) return send(413, 'Too large');
    const common = { 'cache-control': 'private, max-age=60', 'content-type': type };
    if (/text\/html|application\/xhtml/i.test(type)) {
      const m = /charset=([^;]+)/i.exec(type); const text = new TextDecoder((m && m[1].trim()) || 'utf-8', { fatal: false }).decode(buf);
      return send(up.status, rewriteHtml(text, url.href), { ...common, 'content-type': 'text/html; charset=utf-8' });
    }
    return send(up.status, buf, common);
  } catch (err) {
    return send(err.status || 502, `Proxy error: ${err.status ? err.message : 'could not fetch that page'}`);
  }
}

module.exports = { handle, sign, verify, isPrivateIp, rewriteHtml };
