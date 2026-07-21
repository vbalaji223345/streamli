import streamlit as st
from streamlit.components.v1 import html
import pandas as pd
import subprocess
import os
import tempfile
import io
import re
import json as _json_mod
import time
from datetime import datetime
from zoneinfo import ZoneInfo

# Apply theme before any rendering
if st.session_state.get("dark_mode", False):
  st._config.set_option("theme.base", "dark")
  st._config.set_option("theme.backgroundColor", "#0e1117")
  st._config.set_option("theme.secondaryBackgroundColor", "#1e2130")
  st._config.set_option("theme.textColor", "#fafafa")
  st._config.set_option("theme.primaryColor", "#4a9eff")
else:
  st._config.set_option("theme.base", "light")
  st._config.set_option("theme.backgroundColor", "#ffffff")
  st._config.set_option("theme.secondaryBackgroundColor", "#f0f2f6")
  st._config.set_option("theme.textColor", "#262730")
  st._config.set_option("theme.primaryColor", "#ff4b4b")


def generate_short_month_id(prefix):
    ist_tz = ZoneInfo("Asia/Kolkata")
    timestamp = datetime.now(ist_tz).strftime("%b%d%H%M%S")
    return f"{prefix}_{timestamp}"

# -------------------------
# 1. Page Configuration
# -------------------------
st.set_page_config(page_title="BBW Violet Chatbot", page_icon="🛀", layout="centered", initial_sidebar_state="expanded")

#to hide fork and git hub icons with full hamburger menu
lock_sidebar_css = """
    <style>

        [data-testid="stToolbar"] {
            display: none !important;
        }

        [data-testid="stSidebarCollapseButton"] {
            display: none !important;
        }

        [data-testid="collapsedControl"] {
            display: none !important;
        }
    </style>
"""
st.markdown(lock_sidebar_css, unsafe_allow_html=True)

#To hide footer
hide_st_style = """
    <style>
    footer { visibility: hidden;}
    </style>
"""
st.markdown(hide_st_style,unsafe_allow_html=True)

html(
    """
    <script>
    window.parent.document.querySelectorAll('[href*="streamlit.io"]').forEach(e => e.setAttribute("style", "display: none;"));

    (function() {
      var D = window.parent.document;

      function ensureTip() {
        var t = D.getElementById('__lat_tip__');
        if (!t) {
          t = D.createElement('div');
          t.id = '__lat_tip__';
          t.style.cssText = 'display:none;position:fixed;z-index:99999;background:#ffffff;color:#24292f;border:1px solid #d0d7de;border-radius:8px;border-top:3px solid #0969da;padding:10px 14px;white-space:nowrap;font-family:monospace;font-size:12px;box-shadow:0 4px 16px rgba(0,0,0,0.12);pointer-events:none;';
          D.body.appendChild(t);
        }
        return t;
      }

      function showTip(el) {
        try {
          var dataEl = el.querySelector('.lat-data');
          if (!dataEl) return;
          var data = JSON.parse(dataEl.textContent);
          var tip = ensureTip();
          var BAR = 160;

          // Per-row accent colors for timing phases
          var ROW_COLOR = {
            'DNS Lookup':        '#0969da',
            'TCP Handshake':     '#0891b2',
            'TLS Handshake':     '#8250df',
            'Server Processing': '#e16f24',
            'Total Time':        '#1a7f37',
            'HTTP Status':       '#57606a',
            'HTTP Version':      '#57606a',
            'Server IP':         '#57606a',
            'Sent':              '#57606a',
            'Received':          '#57606a',
            'Download Speed':    '#57606a',
          };

          function toMs(v) {
            if (!v || v === 'Cache') return null;
            var m = String(v).match(/([\d.]+)\s*(ms|s)$/);
            if (!m) return null;
            return parseFloat(m[1]) * (m[2] === 's' ? 1000 : 1);
          }

          var keys = Object.keys(data);
          var maxMs = 0;
          keys.forEach(function(k) {
            if (k !== 'Total Time' && data[k] !== null) {
              var ms = toMs(data[k]); if (ms && ms > maxMs) maxMs = ms;
            }
          });

          var h = '<table style="border-collapse:collapse">'
            + '<tr>'
            + '<th style="color:#57606a;font-size:11px;font-weight:600;letter-spacing:.05em;padding:2px 0 6px;border-bottom:2px solid #d0d7de;min-width:140px">EVENT</th>'
            + '<th style="min-width:' + BAR + 'px;padding:2px 12px 6px;border-bottom:2px solid #d0d7de"></th>'
            + '<th style="color:#57606a;font-size:11px;font-weight:600;letter-spacing:.05em;padding:2px 0 6px;text-align:right;border-bottom:2px solid #d0d7de">VALUE</th>'
            + '</tr>';

          keys.forEach(function(k) {
            var v = data[k];

            // Separator row
            if (v === null) {
              h += '<tr><td colspan="3" style="padding:4px 0;"><div style="height:1px;background:linear-gradient(to right,#d0d7de,#eaeef2)"></div></td></tr>';
              return;
            }

            var isTotal = k === 'Total Time';
            var isCache = v === 'Cache';
            var ms = toMs(v);
            var pt = isTotal ? '7' : '4';
            var topB = isTotal ? ';border-top:2px solid #d0d7de' : '';
            var rowColor = ROW_COLOR[k] || '#24292f';
            var txtColor = isTotal ? rowColor : '#24292f';

            // Colored dot + label
            var dot = isTotal ? '' : '<span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:' + rowColor + ';margin-right:6px;vertical-align:middle"></span>';

            // HTTP Status colour
            var displayVal;
            if (k === 'HTTP Status') {
              var code = parseInt(v, 10);
              var sc = code >= 500 ? '#cf222e' : code >= 400 ? '#9a6700' : code >= 200 ? '#1a7f37' : '#57606a';
              var sbg = code >= 500 ? '#ffebe9' : code >= 400 ? '#fff8c5' : code >= 200 ? '#dafbe1' : '#f6f8fa';
              displayVal = '<span style="color:' + sc + ';background:' + sbg + ';font-weight:600;padding:1px 6px;border-radius:10px;border:1px solid ' + sc + '33">' + v + '</span>';
            } else if (isCache) {
              displayVal = '<span style="color:#8c959f;background:#f6f8fa;padding:1px 6px;border-radius:10px">Cache</span>';
            } else if (isTotal) {
              displayVal = '<span style="color:' + rowColor + ';font-weight:700;font-size:13px">' + v + '</span>';
            } else {
              displayVal = '<span style="color:' + rowColor + ';font-weight:600">' + v + '</span>';
            }

            var barCell;
            if (isTotal) {
              barCell = '<td style="padding:' + pt + 'px 12px' + topB + '"></td>';
            } else if (!ms) {
              barCell = '<td style="padding:' + pt + 'px 12px;min-width:' + BAR + 'px"></td>';
            } else {
              var fw = maxMs > 0 ? Math.max(3, Math.round((ms / maxMs) * BAR)) : 3;
              barCell = '<td style="padding:' + pt + 'px 12px">'
                + '<div style="width:' + BAR + 'px;height:8px;background:#eaeef2;border-radius:4px">'
                + '<div style="width:' + fw + 'px;height:100%;background:' + rowColor + ';border-radius:4px;opacity:0.85"></div>'
                + '</div></td>';
            }

            h += '<tr style="' + (isTotal ? 'background:#f0fff4' : '') + '">'
              + '<td style="padding:' + pt + 'px 14px ' + pt + 'px 0;white-space:nowrap' + topB + '">' + dot + '<span style="color:' + (isTotal ? rowColor : '#24292f') + (isTotal?';font-weight:700':';font-weight:500') + '">' + k + '</span></td>'
              + barCell
              + '<td style="text-align:right;padding:' + pt + 'px 0;white-space:nowrap' + topB + '">' + displayVal + '</td>'
              + '</tr>';
          });

          h += '</table>';
          tip.innerHTML = h;
          tip.style.display = 'block';
          var r = el.getBoundingClientRect();
          var left = r.left + r.width / 2 - tip.offsetWidth / 2;
          var top = r.top - tip.offsetHeight - 8;
          if (top < 0) top = r.bottom + 8;
          tip.style.left = Math.max(4, Math.min(left, window.parent.innerWidth - tip.offsetWidth - 4)) + 'px';
          tip.style.top  = top + 'px';
        } catch(e) {}
      }

      function hideTip() {
        var t = D.getElementById('__lat_tip__');
        if (t) t.style.display = 'none';
      }

      // 4. Badge count-up animation
      function animateBadgeCountUp(el) {
        var badgeSpan = el.firstElementChild;
        if (!badgeSpan) return;
        var walker = D.createTreeWalker(badgeSpan, NodeFilter.SHOW_TEXT, null, false);
        var timeNode = null, node;
        while ((node = walker.nextNode())) {
          if (/[\d.]+\s*(ms|s)/.test(node.textContent)) { timeNode = node; break; }
        }
        if (!timeNode) return;
        var origText = timeNode.textContent;
        var match = origText.match(/([\d.]+)\s*(ms|s)/);
        if (!match) return;
        var target = parseFloat(match[1]), unit = match[2];
        var dur = Math.min(900, 150 + target * 0.4);
        var t0 = performance.now();
        (function tick(now) {
          var p = Math.min((now - t0) / dur, 1);
          var e = 1 - Math.pow(1 - p, 3);
          var val = unit === 'ms' ? Math.round(e * target) + ' ms' : (e * target).toFixed(2) + ' s';
          timeNode.textContent = origText.replace(match[0], val);
          if (p < 1) requestAnimationFrame(tick); else timeNode.textContent = origText;
        })(t0);
      }

      function bindBadges() {
        D.querySelectorAll('.lat-badge-wrap:not([data-lb])').forEach(function(el) {
          el.setAttribute('data-lb', '1');
          el.addEventListener('mouseenter', function() { showTip(this); });
          el.addEventListener('mouseleave', function() { hideTip(); });
          animateBadgeCountUp(el);
          // 7. Turn number pop
          var turnSpan = el.querySelector('span[style*="color:#888"]');
          if (turnSpan) {
            turnSpan.style.display = 'inline-block';
            turnSpan.style.animation = 'turnPop 0.4s cubic-bezier(.36,1.6,.46,1) both';
          }
        });
      }

      bindBadges();

      // Color-coded verdict buttons
      var VERDICT_COLORS = {
        'RAI Safe':                 { bg: '#27ae60', border: '#1e8449' },
        'RAI High Risk':            { bg: '#e74c3c', border: '#c0392b' },
        'RAI Low Risk':             { bg: '#e67e22', border: '#ca6f1e' },
        'Unknown':                  { bg: '#7f8c8d', border: '#616a6b' },
        'Customer Treatment Error': { bg: '#8e44ad', border: '#7d3c98' },
        'Functional Error':         { bg: '#2980b9', border: '#2471a3' },
      };
      function colorVerdictButtons() {
        D.querySelectorAll('[data-testid="stChatMessage"] button').forEach(function(btn) {
          var pEl = btn.querySelector('p');
          var txt = (pEl ? pEl.textContent : btn.textContent).trim();
          var c = VERDICT_COLORS[txt];
          if (!c) return;
          btn.style.setProperty('background-color', c.bg, 'important');
          btn.style.setProperty('border-color', c.border, 'important');
          btn.style.setProperty('color', '#fff', 'important');
          btn.style.setProperty('font-weight', '600', 'important');
          // Selected (primary) gets a glow
          if (btn.getAttribute('kind') === 'primary' || btn.getAttribute('data-testid') === 'baseButton-primary') {
            btn.style.setProperty('box-shadow', '0 0 0 3px ' + c.bg + '55', 'important');
          }
        });
      }
      colorVerdictButtons();


      // ── Animated dark-mode toggle ──
      function setupDMToggle() {
        var sidebar = D.querySelector('[data-testid="stSidebar"]');
        if (!sidebar) return;
        var cbWrap = sidebar.querySelector('[data-testid="stCheckbox"]');
        if (!cbWrap || cbWrap.getAttribute('data-dm-rdy')) return;
        var cbInput = cbWrap.querySelector('input[type="checkbox"]');
        var cbLabel = cbWrap.querySelector('[data-baseweb="checkbox"]');
        if (!cbInput || !cbLabel) return;
        cbWrap.setAttribute('data-dm-rdy', '1');

        var toggle = D.createElement('div');
        toggle.style.cssText = 'display:flex;align-items:center;gap:12px;cursor:pointer;padding:6px 2px;';

        var track = D.createElement('div');
        track.style.cssText = 'position:relative;width:52px;height:28px;border-radius:14px;flex-shrink:0;transition:background 0.35s ease;box-shadow:inset 0 1px 3px rgba(0,0,0,0.2);';

        var knob = D.createElement('div');
        knob.style.cssText = 'position:absolute;top:3px;left:3px;width:22px;height:22px;border-radius:50%;background:#fff;box-shadow:0 1px 5px rgba(0,0,0,0.35);display:flex;align-items:center;justify-content:center;font-size:14px;line-height:1;transition:transform 0.35s cubic-bezier(.4,0,.2,1);';

        var lbl = D.createElement('span');
        lbl.style.cssText = 'font-size:14px;font-weight:500;';

        function applyState(checked) {
          track.style.background = checked ? '#4a9eff' : '#bbb';
          knob.style.transform = checked ? 'translateX(24px)' : 'translateX(0)';
          knob.textContent = checked ? '🌙' : '☀️';
          lbl.textContent = checked ? 'Dark Mode' : 'Light Mode';
        }
        applyState(cbInput.checked);

        track.appendChild(knob);
        toggle.appendChild(track);
        toggle.appendChild(lbl);
        // Keep label in DOM so React events still fire, just make it invisible
        cbLabel.style.cssText = 'opacity:0;position:absolute;width:0;height:0;overflow:hidden;pointer-events:none;';
        cbWrap.appendChild(toggle);

        toggle.addEventListener('click', function() {
          applyState(!cbInput.checked);
          setTimeout(function() { cbInput.click(); }, 320);
        });
      }
      setupDMToggle();

      // 3. Confetti burst on verdict click
      function burstConfetti(x, y) {
        var colors = ['#ff4b4b','#27ae60','#4a9eff','#e67e22','#8e44ad','#f1c40f','#e74c3c','#2ecc71'];
        for (var i = 0; i < 22; i++) {
          var p = D.createElement('div');
          var angle = Math.random() * 360;
          var dist = 35 + Math.random() * 55;
          var size = 5 + Math.random() * 6;
          p.style.cssText = 'position:fixed;z-index:99999;pointer-events:none;width:'+size+'px;height:'+size+'px;background:'+colors[i%colors.length]+';border-radius:'+(Math.random()>.5?'50%':'3px')+';left:'+x+'px;top:'+y+'px;';
          D.body.appendChild(p);
          var dx = Math.cos(angle*Math.PI/180)*dist, dy = Math.sin(angle*Math.PI/180)*dist - 28;
          p.animate([
            {transform:'translate(-50%,-50%) scale(1)',opacity:1},
            {transform:'translate(calc(-50% + '+dx+'px),calc(-50% + '+dy+'px)) scale(0)',opacity:0}
          ],{duration:650,easing:'cubic-bezier(0,.9,.57,1)',fill:'forwards'});
          setTimeout((function(el){return function(){el.remove()};})(p), 700);
        }
      }
      function popCheckmark(x, y) {
        var ck = D.createElement('span');
        ck.textContent = '✓';
        ck.style.cssText = 'position:fixed;z-index:99999;font-size:22px;font-weight:bold;color:#27ae60;left:'+x+'px;top:'+y+'px;pointer-events:none;animation:checkPop 0.65s ease-out forwards;';
        D.body.appendChild(ck);
        setTimeout(function(){ck.remove();}, 700);
      }
      function setupVerdictConfetti() {
        D.querySelectorAll('[data-testid="stChatMessage"] button:not([data-cf])').forEach(function(btn) {
          var pEl = btn.querySelector('p');
          var txt = (pEl?pEl.textContent:btn.textContent).trim();
          if (!VERDICT_COLORS[txt]) return;
          btn.setAttribute('data-cf','1');
          btn.addEventListener('click', function() {
            var r = btn.getBoundingClientRect();
            burstConfetti(r.left+r.width/2, r.top+r.height/2);
            popCheckmark(r.left+r.width/2, r.top+r.height/2);
          });
        });
      }
      setupVerdictConfetti();

      // 5. Typewriter reveal + 1. avatar wobble + 10. border glow for new messages
      function setupTypewriter() {
        var msgs = D.querySelectorAll('[data-testid="stChatMessage"]');
        if (window.parent.__twCount === undefined) { window.parent.__twCount = msgs.length; return; }
        if (msgs.length > window.parent.__twCount) {
          for (var i = window.parent.__twCount; i < msgs.length; i++) {
            // 5. typewriter
            var c = msgs[i].querySelector('[data-testid="stMarkdownContainer"]');
            if (c) { c.style.opacity='0'; c.style.animation='twReveal 0.45s ease 0.05s both'; }
          }
          // 10. border glow using Web Animations API (avoids CSS animation conflict)
          var bw = D.querySelector('[data-testid="stVerticalBlockBorderWrapper"]');
          if (bw) {
            bw.animate([
              {boxShadow:'0 0 0 0 rgba(74,158,255,0.6)'},
              {boxShadow:'0 0 0 8px rgba(74,158,255,0.3)'},
              {boxShadow:'0 0 0 0 rgba(74,158,255,0)'}
            ], {duration:1000, easing:'ease-out'});
          }
          window.parent.__twCount = msgs.length;
        }
      }
      setupTypewriter();

      // 6. Send ripple on chat input submit
      function setupSendRipple() {
        var ta = D.querySelector('[data-testid="stChatInput"] textarea');
        if (!ta || ta.getAttribute('data-rp')) return;
        ta.setAttribute('data-rp','1');
        var hadText = false;
        ta.addEventListener('input', function() { hadText = this.value.length > 0; });
        ta.addEventListener('keydown', function(e) {
          if (e.key==='Enter' && !e.shiftKey && hadText) {
            var ct = D.querySelector('[data-testid="stChatInput"]');
            if (ct) { ct.style.animation='none'; ct.offsetHeight; ct.style.animation='sendRipple 0.6s ease-out'; }
          }
        });
      }
      setupSendRipple();

      // 3. Input flash on blur (User ID / Session ID fields)
      function setupInputFlash() {
        var sidebar = D.querySelector('[data-testid="stSidebar"]');
        if (!sidebar) return;
        sidebar.querySelectorAll('input[type="text"]:not([data-if])').forEach(function(inp) {
          inp.setAttribute('data-if','1');
          inp.addEventListener('blur', function() {
            if (this.value.trim()) {
              // Animate the baseweb wrapper — Streamlit overrides box-shadow on the raw input
              var wrap = this.closest('[data-baseweb="input"]') || this.parentElement;
              wrap.animate([
                {boxShadow:'0 0 0 0 rgba(39,174,96,.75)'},
                {boxShadow:'0 0 0 9px rgba(39,174,96,0)'}
              ], {duration:600, easing:'ease-out'});
            }
          });
        });
      }
      setupInputFlash();

      // 5. Chat container entrance (one-time on load)
      function setupContainerEntrance() {
        if (window.parent.__containerEntered) return;
        window.parent.__containerEntered = true;
        var bw = D.querySelector('[data-testid="stVerticalBlockBorderWrapper"]');
        if (bw) { bw.style.animation = 'containerSlideDown 0.5s ease-out both'; }
      }
      setupContainerEntrance();

      // 6. Metric flip on API count change
      function setupMetricFlip() {
        var mv = D.querySelector('[data-testid="stSidebar"] [data-testid="stMetricValue"]');
        if (!mv) return;
        var cur = mv.textContent.trim();
        if (window.parent.__metricVal !== undefined && window.parent.__metricVal !== cur) {
          mv.style.display = 'inline-block';
          var par = mv.parentElement;
          if (par) par.style.perspective = '200px';
          mv.style.animation='none'; mv.offsetHeight; mv.style.animation='metricFlip 0.5s ease';
        }
        window.parent.__metricVal = cur;
      }
      setupMetricFlip();

      // helper: first h1 outside sidebar
      function getMainH1() {
        var all = D.querySelectorAll('h1');
        for (var k = 0; k < all.length; k++) {
          if (!all[k].closest('[data-testid="stSidebar"]')) return all[k];
        }
        return null;
      }



      // Title hover: emoji spin only (slow → fast on hover, stops on leave)
      function setupTitleHover() {
        var h1 = getMainH1();
        if (!h1) return;
        // Re-run if: new element OR React removed our spin span
        var W = window.parent;
        if (W.__thH1 === h1 && h1.querySelector('.th-spin-em')) return;

        // Remove stale listeners from previous setup
        if (W.__thEnterFn) h1.removeEventListener('mouseenter', W.__thEnterFn);
        if (W.__thLeaveFn) h1.removeEventListener('mouseleave', W.__thLeaveFn);
        W.__thH1 = h1;

        // Wrap the leading emoji in a spin span (re-insert if React removed it)
        if (!h1.querySelector('.th-spin-em')) {
          var fc = [...h1.textContent][0];
          if (fc) h1.innerHTML = h1.innerHTML.replace(fc,
            '<span class="th-spin-em" style="display:inline-block;transform-origin:center">'+fc+'</span>');
        }
        if (!h1.querySelector('.th-spin-em')) return;

        var isHovering = false, spinRAF = null, spinAngle = 0, spinSpeed = 0;

        function spinLoop() {
          if (!isHovering) return;
          spinSpeed = Math.min(spinSpeed + 0.22, 24);
          spinAngle += spinSpeed;
          var el = h1.querySelector('.th-spin-em');
          if (el) el.style.transform = 'rotate('+spinAngle+'deg)';
          spinRAF = requestAnimationFrame(spinLoop);
        }

        function onEnter() { isHovering = true; spinSpeed = 0.5; spinLoop(); }
        function onLeave() {
          isHovering = false;
          cancelAnimationFrame(spinRAF);
          var el = h1.querySelector('.th-spin-em');
          if (el) el.style.transform = 'rotate(0deg)';
        }

        W.__thEnterFn = onEnter;
        W.__thLeaveFn = onLeave;
        h1.addEventListener('mouseenter', onEnter);
        h1.addEventListener('mouseleave', onLeave);
      }
      setupTitleHover();

      // 8. Retry button heartbeat
      function setupRetryHeartbeat() {
        D.querySelectorAll('[data-testid="stChatMessage"] button:not([data-hb])').forEach(function(btn) {
          var pEl = btn.querySelector('p');
          var txt = (pEl?pEl.textContent:btn.textContent).trim();
          if (!txt.includes('Retry')) return;
          btn.setAttribute('data-hb','1');
          btn.style.animation = 'heartbeat 1.5s ease-in-out 2';
        });
      }
      setupRetryHeartbeat();

      // Reconnect observer each time this script runs (iframe may be recreated on rerun)
      if (window.parent.__latObs) { try { window.parent.__latObs.disconnect(); } catch(e) {} }
      var obs = new MutationObserver(function() {
        bindBadges(); colorVerdictButtons(); setupDMToggle();
        setupVerdictConfetti(); setupTypewriter(); setupSendRipple();
        setupInputFlash(); setupMetricFlip(); setupRetryHeartbeat(); setupTitleHover();
      });
      obs.observe(D.body, { childList: true, subtree: true });
      window.parent.__latObs = obs;

      // Auto-focus chat input when user starts typing from anywhere on the page
      if (window.parent.__autoFocusHandler) {
        try { D.removeEventListener('keydown', window.parent.__autoFocusHandler); } catch(e) {}
      }
      window.parent.__autoFocusHandler = function(e) {
        if (e.key.length !== 1) return;
        if (e.ctrlKey || e.metaKey || e.altKey) return;
        var active = D.activeElement;
        if (active) {
          var tag = active.tagName;
          if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
          if (active.isContentEditable) return;
        }
        // Find the chat textarea — try specific selectors then fall back to any enabled textarea
        var chatInput = D.querySelector('[data-testid="stChatInput"] textarea')
                     || D.querySelector('[data-testid="stChatInputTextArea"]')
                     || (function() {
                          var all = D.querySelectorAll('textarea');
                          for (var i = 0; i < all.length; i++) {
                            if (!all[i].disabled) return all[i];
                          }
                          return null;
                        })();
        if (!chatInput || chatInput.disabled) return;
        e.preventDefault();
        chatInput.focus();
        // execCommand triggers React's synthetic input event reliably
        try { D.execCommand('insertText', false, e.key); } catch(err) {}
      };
      D.addEventListener('keydown', window.parent.__autoFocusHandler);

      // Orange "ready" border when chat input transitions from disabled → enabled
      if (window.parent.__readyObs) { try { window.parent.__readyObs.disconnect(); } catch(e) {} }
      (function() {
        function setupReadyWatch() {
          var chatInput = D.querySelector('[data-testid="stChatInput"] textarea')
                       || (function() { var all = D.querySelectorAll('textarea'); for (var i = 0; i < all.length; i++) { if (all[i]) return all[i]; } return null; })();
          if (!chatInput) return false;
          var container = chatInput.closest('[data-testid="stChatInput"]') || chatInput.parentElement;
          window.parent.__readyObs = new MutationObserver(function(mutations) {
            mutations.forEach(function(m) {
              if (m.attributeName === 'disabled') {
                if (!chatInput.disabled) {
                  container.classList.add('lat-ready');
                  chatInput.addEventListener('focus', function() {
                    container.classList.remove('lat-ready');
                  }, { once: true });
                } else {
                  container.classList.remove('lat-ready');
                }
              }
            });
          });
          window.parent.__readyObs.observe(chatInput, { attributes: true, attributeFilter: ['disabled'] });
          return true;
        }
        if (!setupReadyWatch()) {
          var waitObs = new MutationObserver(function() { if (setupReadyWatch()) waitObs.disconnect(); });
          waitObs.observe(D.body, { childList: true, subtree: true });
        }
      })();
    })();
    </script>
    """,
    height=0,
)

# -------------------------
# 2. Custom CSS
# -------------------------
st.markdown("""
  <style>
    [data-testid="stChatMessage"] {
      padding-top: 0.5rem !important;
      padding-bottom: 0.5rem !important;
    }
    .stStatusWidget { display: none !important; }
    .block-container { padding-top: 2rem !important; }
    hr { margin: 1em 0px !important; }
    .uid-tooltip-wrap {
      position: relative;
      display: inline-block;
    }
    .uid-info-icon {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 15px;
      height: 15px;
      background: #4a9eff;
      color: white;
      border-radius: 50%;
      font-size: 10px;
      font-weight: bold;
      font-style: normal;
      cursor: pointer;
      vertical-align: middle;
      margin-left: 5px;
    }
    .uid-tooltip-text {
      visibility: hidden;
      opacity: 0;
      background: #1e2a3a;
      color: #e0e0e0;
      border-radius: 6px;
      padding: 10px 12px;
      position: absolute;
      z-index: 99999;
      left: 120%;
      top: -8px;
      width: 340px;
      font-size: 12px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.4);
      transition: opacity 0.2s;
      pointer-events: none;
    }
    .uid-tooltip-text table {
      border-collapse: collapse;
      width: 100%;
    }
    .uid-tooltip-text th {
      color: #7ec8ff;
      padding: 3px 8px;
      text-align: left;
      border-bottom: 1px solid #3a4a5a;
    }
    .uid-tooltip-text td {
      padding: 3px 8px;
      border-bottom: 1px solid #2a3a4a;
    }
    .uid-tooltip-text .tt-title {
      font-weight: bold;
      color: #7ec8ff;
      margin-bottom: 6px;
      display: block;
    }
    .uid-tooltip-wrap:hover .uid-tooltip-text {
      visibility: visible;
      opacity: 1;
    }
[data-testid="stChatInput"]:focus-within {
      border: 1.5px solid #4a9eff !important;
      box-shadow: 0 0 0 3px rgba(74, 158, 255, 0.18) !important;
      border-radius: 10px !important;
      transition: box-shadow 0.15s, border-color 0.15s;
    }
    [data-testid="stChatInput"].lat-ready {
      border: 1.5px solid #e16f24 !important;
      box-shadow: 0 0 0 4px rgba(225, 111, 36, 0.22) !important;
      border-radius: 10px !important;
      animation: latReadyPulse 1s ease-in-out 3;
    }
    @keyframes latReadyPulse {
      0%, 100% { box-shadow: 0 0 0 3px rgba(225, 111, 36, 0.18) !important; }
      50%       { box-shadow: 0 0 0 7px rgba(225, 111, 36, 0.35) !important; }
    }
    /* 5. Typewriter reveal for new messages */
    @keyframes twReveal { from{opacity:0;transform:translateY(4px)} to{opacity:1;transform:translateY(0)} }
    /* 6. Send ripple */
    @keyframes sendRipple { 0%{box-shadow:0 0 0 0 rgba(74,158,255,.6)} 100%{box-shadow:0 0 0 20px rgba(74,158,255,0)} }
    /* 7. Turn number pop */
    @keyframes turnPop { from{transform:scale(0.4);opacity:0} to{transform:scale(1);opacity:1} }
/* 4. Progress bar striped march */
    [data-testid="stProgressBar"] > div { overflow:hidden; }
    [data-testid="stProgressBar"] > div > div { background-image:repeating-linear-gradient(45deg,transparent,transparent 8px,rgba(255,255,255,0.18) 8px,rgba(255,255,255,0.18) 16px) !important; background-size:22px 22px; animation:stripesMarch 0.7s linear infinite; border-radius:4px; }
    @keyframes stripesMarch { from{background-position:0 0} to{background-position:22px 0} }
    /* 5. Container entrance */
    @keyframes containerSlideDown { from{opacity:0;transform:translateY(-12px)} to{opacity:1;transform:translateY(0)} }
    /* 6. Metric flip */
    @keyframes metricFlip { 0%{transform:rotateX(0deg)} 40%{transform:rotateX(90deg);opacity:0} 41%{transform:rotateX(-90deg);opacity:0} 100%{transform:rotateX(0deg);opacity:1} }
    /* 7b. Checkmark pop */
    @keyframes checkPop { 0%{transform:translate(-50%,-50%) scale(0);opacity:1} 60%{transform:translate(-50%,-130%) scale(1.4);opacity:1} 100%{transform:translate(-50%,-200%) scale(1);opacity:0} }
    /* 8. Retry heartbeat */
    @keyframes heartbeat { 0%,100%{transform:scale(1)} 14%{transform:scale(1.12)} 28%{transform:scale(1)} 42%{transform:scale(1.07)} 70%{transform:scale(1)} }
    /* 2. Verdict button hover shimmer */
    @keyframes shimmerSweep { 0%{left:-75%} 100%{left:125%} }
    [data-testid="stChatMessage"] button {
      font-size: 8px !important;
      padding: 1px 3px !important;
      min-height: 0px !important;
      height: 22px !important;
      line-height: 1 !important;
      white-space: nowrap !important;
      overflow: hidden !important;
      text-overflow: ellipsis !important;
      position: relative !important;
    }
    [data-testid="stChatMessage"] button::after {
      content: '';
      position: absolute;
      top: 0; left: -75%;
      width: 50%; height: 100%;
      background: linear-gradient(to right, transparent, rgba(255,255,255,0.28), transparent);
      transform: skewX(-20deg);
      pointer-events: none;
    }
    [data-testid="stChatMessage"] button:hover::after { animation: shimmerSweep 1.4s linear infinite; }
  </style>
""", unsafe_allow_html=True)

if st.session_state.get("dark_mode", False):
  st.markdown("""
    <style>
      /* Latency badge — boost contrast in dark mode */
      .lat-badge-wrap span[style*="border-radius:12px"],
      span[style*="border-radius:12px"][style*="font-family:monospace"] {
        filter: brightness(1.3) !important;
      }
    </style>
  """, unsafe_allow_html=True)

# -------------------------
# 3. Model Logic
# -------------------------
_API_URL = "https://cognigy-endpoint-na1.nicecxone.com/6941693df79d403a8afa34f8c98242e8dd90d62546734ebf1e20870a6d143953"

def call_model(prompt: str, user_id: str, session_id: str) -> tuple[str, float, dict]:
  st.session_state.api_call_count += 1
  body_path = resp_path = None
  try:
    data = {"userId": user_id, "sessionId": session_id, "text": prompt}

    body_fd, body_path = tempfile.mkstemp(suffix=".json")
    os.close(body_fd)
    resp_fd, resp_path = tempfile.mkstemp(suffix=".json")
    os.close(resp_fd)

    with open(body_path, "w", encoding="utf-8") as f:
      _json_mod.dump(data, f)

    _CURL_W = "|".join([
      "%{time_namelookup}", "%{time_connect}", "%{time_appconnect}",
      "%{time_starttransfer}", "%{time_total}",
      "%{http_code}", "%{http_version}", "%{remote_ip}",
      "%{size_upload}", "%{size_download}", "%{speed_download}",
    ])

    result = subprocess.run(
      [
        "curl", "-s",
        "-X", "POST",
        "-H", "Content-Type: application/json",
        "-d", f"@{body_path}",
        "-o", resp_path,
        "-w", _CURL_W,
        "--max-time", "120",
        _API_URL,
      ],
      capture_output=True, text=True, timeout=125,
    )

    parts = [p.replace(",", ".") for p in result.stdout.strip().split("|")]
    t_dns, t_tcp, t_tls, t_start, t_total = (float(p) for p in parts[:5])
    http_code    = parts[5].strip()
    http_ver_raw = parts[6].strip()
    remote_ip    = parts[7].strip() or "—"
    size_up      = int(float(parts[8]))
    size_dn      = int(float(parts[9]))
    speed_dn     = float(parts[10])

    http_version = http_ver_raw if http_ver_raw.upper().startswith("HTTP") else f"HTTP/{http_ver_raw}"

    def _fmtb(b):
      if b < 1024:          return f"{b} B"
      if b < 1024 * 1024:   return f"{b/1024:.2f} KB"
      return                       f"{b/1024/1024:.2f} MB"

    def _fmtspd(bps):
      if bps < 1024:        return f"{bps:.0f} B/s"
      if bps < 1024 * 1024: return f"{bps/1024:.2f} KB/s"
      return                       f"{bps/1024/1024:.2f} MB/s"

    with open(resp_path, "r", encoding="utf-8") as f:
      response_text = _json_mod.load(f).get("text", "No response text found.")

    timing_details = {
      "DNS Lookup":        f"{t_dns:.6f}s",
      "TCP Handshake":     f"{t_tcp:.6f}s",
      "TLS Handshake":     f"{t_tls:.6f}s",
      "Server Processing": f"{t_start:.6f}s",
      "Total Time":        f"{t_total:.6f}s",
      "__sep__":           None,
      "HTTP Status":       http_code,
      "HTTP Version":      http_version,
      "Server IP":         remote_ip,
      "Sent":              _fmtb(size_up),
      "Received":          _fmtb(size_dn),
      "Download Speed":    _fmtspd(speed_dn),
    }
    return response_text, t_total * 1000, timing_details

  except Exception as e:
    return f"Error connecting to model: {e}", 0.0, {}
  finally:
    for p in (body_path, resp_path):
      try:
        if p: os.unlink(p)
      except OSError:
        pass

def latency_badge(ms: float, turn: int | None = None, timing_details: dict | None = None) -> str:
  if ms <= 3000:
    color, bg = "#1a7f37", "#dafbe1"
  elif ms <= 5000:
    color, bg = "#9a6700", "#fff8c5"
  else:
    color, bg = "#cf222e", "#ffebe9"
  label = f"{ms:.0f} ms" if ms < 1000 else f"{ms/1000:.2f} s"
  turn_tag = f'<span style="color:#888;font-weight:400;">Turn {turn}&nbsp;&nbsp;</span>' if turn is not None else ""
  badge = (
    f'<span style="display:inline-flex;align-items:center;gap:4px;padding:2px 10px;border-radius:12px;'
    f'font-size:11px;font-weight:600;color:{color};background:{bg};'
    f'border:1px solid {color}33;font-family:monospace;margin-top:4px;">'
    f'{turn_tag}⏱ {label}</span>'
  )
  if not timing_details:
    return badge
  tip_json = _json_mod.dumps(timing_details)
  return (
    '<span class="lat-badge-wrap" style="display:inline-block;cursor:pointer">'
    + badge
    + f'<span class="lat-data" style="display:none">{tip_json}</span>'
    + '</span>'
  )

# -------------------------
# 4. Session State Initialization
# -------------------------
if "chat_history" not in st.session_state:
  st.session_state.chat_history = []
if "results" not in st.session_state:
  st.session_state.results = []
if "processing_done" not in st.session_state:
  st.session_state.processing_done = False
if "is_processing" not in st.session_state:
  st.session_state.is_processing = False
if "generated_user_id" not in st.session_state:
  st.session_state.generated_user_id = ""
if "generated_session_id" not in st.session_state:
  st.session_state.generated_session_id = ""
if "api_call_count" not in st.session_state:
  st.session_state.api_call_count = 0
if "verdicts" not in st.session_state:
  st.session_state.verdicts = {}
if "batch_pending" not in st.session_state:
  st.session_state.batch_pending = False
if "is_responding" not in st.session_state:
  st.session_state.is_responding = False
if "pending_manual_prompt" not in st.session_state:
  st.session_state.pending_manual_prompt = None
if "pending_retry" not in st.session_state:
  st.session_state.pending_retry = None
if "dark_mode" not in st.session_state:
  st.session_state.dark_mode = False

# -------------------------
# 5. SIDEBAR: Controls & Credentials (UPDATED)
# -------------------------
with st.sidebar:
  st.title("🛀 Violet Controls")
  st.metric(label="🔢 API Calls This Session", value=st.session_state.api_call_count)

  _dm_checked = st.checkbox("🌙 Dark Mode", value=st.session_state.dark_mode, key="dm_toggle_cb")
  if _dm_checked != st.session_state.dark_mode:
    st.session_state.dark_mode = _dm_checked
    st.rerun()

  st.subheader("BBW User details")
  prefix_input = st.text_input("Enter Prefix", placeholder="e.g. B")

  if st.button("🔑 Generate IDs", use_container_width=True):
    if prefix_input.strip():
      st.session_state.generated_user_id = generate_short_month_id(f"{prefix_input}_U")
      st.session_state.generated_session_id = generate_short_month_id(f"{prefix_input}_S")
    else:
      st.warning("Please enter a prefix first.")

  _uid = st.session_state.generated_user_id
  if _uid:
    _ts = _uid.rsplit('_', 1)[-1]   # e.g. "May060851047"
    _month, _day, _hour, _minute, _second = _ts[:3], _ts[3:5], _ts[5:7], _ts[7:9], _ts[9:11]
    try:
      _h = int(_hour)
      _ampm = "AM" if _h < 12 else "PM"
      _h12 = _h % 12 or 12
      _di = int(_day)
      _sfx = "th" if 11 <= _di <= 13 else ["th","st","nd","rd","th","th","th","th","th","th"][_di % 10]
      _hour_meaning = f"The hour in 24-hour time ({_h12}:00 {_ampm})"
      _day_meaning  = f"The day of the month (the {_di}{_sfx})"
    except Exception:
      _hour_meaning, _day_meaning = "The hour in 24-hour time", "The day of the month"
    _month_meaning = f"The month ({_month})"
  else:
    _month = _day = _hour = _minute = _second = "—"
    _month_meaning, _day_meaning, _hour_meaning = "The month", "The day of the month", "The hour in 24-hour time"

  st.markdown(f"""
  <div style="display:flex; align-items:center; margin-bottom:4px;">
    <strong>User ID</strong>
    <span class="uid-tooltip-wrap">
      <i class="uid-info-icon">i</i>
      <span class="uid-tooltip-text">
        <span class="tt-title">Data Breakdown</span>
        <table>
          <tr><th>Segment</th><th>Value</th><th>Meaning</th></tr>
          <tr><td>{_month}</td><td>{_month}</td><td>{_month_meaning}</td></tr>
          <tr><td>{_day}</td><td>{_day}</td><td>{_day_meaning}</td></tr>
          <tr><td>{_hour}</td><td>{_hour}</td><td>{_hour_meaning}</td></tr>
          <tr><td>{_minute}</td><td>{_minute}</td><td>The minute</td></tr>
          <tr><td>{_second}</td><td>{_second}</td><td>The second</td></tr>
        </table>
      </span>
    </span>
  </div>
  """, unsafe_allow_html=True)
  st.session_state.generated_user_id = st.text_input(
    "User ID", value=st.session_state.generated_user_id,
    placeholder="Generate or type manually",
    label_visibility="collapsed"
  )

  st.markdown("**Session ID**")
  st.session_state.generated_session_id = st.text_input(
    "Session ID", value=st.session_state.generated_session_id,
    placeholder="Generate or type manually",
    label_visibility="collapsed"
  )

  u_id = st.session_state.generated_user_id
  s_id = st.session_state.generated_session_id
  
  st.divider()

  if st.button("Generate Id & Clear chat", use_container_width=True):
    if prefix_input.strip():
      st.session_state.generated_user_id = generate_short_month_id(f"{prefix_input}_U")
      st.session_state.generated_session_id = generate_short_month_id(f"{prefix_input}_S")
    else:
      st.warning("Please enter a prefix first.")
    st.session_state.chat_history = []
    st.session_state.results = []
    st.session_state.verdicts = {}
    st.session_state.processing_done = False
    st.session_state.is_processing = False
    st.rerun()

  if st.button("🗑️ Clear All History", use_container_width=True):
    st.session_state.chat_history = []
    st.session_state.results = []
    st.session_state.verdicts = {}
    st.session_state.processing_done = False
    st.session_state.is_processing = False
    st.rerun()
    
  st.divider()
  
  st.subheader("📄 Batch Processing")
  uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx", "xls"])
  prompt_col = st.text_input("Column name", value="prompt")
  
  start_clicked = st.button(
    "▶️ Start Batch Process", 
    disabled=(uploaded_file is None or st.session_state.is_processing),
    use_container_width=True,
    type="primary"
  )

  status_area = st.empty()
  progress_bar = st.empty()
  
  st.divider()
  
  if st.session_state.processing_done or len(st.session_state.results) > 0:
    res_df = pd.DataFrame(st.session_state.results)
    res_df["verdict"] = [st.session_state.verdicts.get(i, "") for i in range(len(st.session_state.results))]
    _excel_buf = io.BytesIO()
    res_df.to_excel(_excel_buf, index=False, engine="openpyxl")
    _excel_buf.seek(0)
    st.download_button(
      label="⬇️ Download Results (Excel)",
      data=_excel_buf,
      file_name="violet_responses.xlsx",
      mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      use_container_width=True
    )

# -------------------------
# 6. MAIN WINDOW: UI
# -------------------------
st.title("🧼BBW Violet local Chatbot⁽ᵖʳᵒᵈ⁾")

_verdict_options = [
  "RAI Safe", "RAI High Risk", "RAI Low Risk",
  "Unknown", "Customer Treatment Error", "Functional Error",
]

def render_history():
  with chat_container:
    if not st.session_state.chat_history:
      st.info("Chat history is empty.")
    else:
      for turn, item in enumerate(st.session_state.chat_history, start=1):
        idx = turn - 1
        avatar = "📄" if item.get("type") == "batch" else "🧑‍💻"
        with st.chat_message("user", avatar=avatar):
          st.write(item['prompt'])
        with st.chat_message("assistant", avatar="🤖"):
          _words = _chars = 0
          if item['response'].strip():
            st.write(item['response'])
            _clean = re.sub(r'\*{1,3}|_{1,3}|`+|#{1,6}\s*|>\s*', '', item['response'])
            _clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', _clean)
            _clean = re.sub(r'\s+', ' ', _clean).strip()
            _words = len(_clean.split())
            _chars = len(_clean)
          else:
            st.warning("⚠️ No response received")
            _locked = st.session_state.is_processing or st.session_state.is_responding
            if not _locked:
              if st.button("🔄 Retry", key=f"retry_{turn}"):
                st.session_state.pending_retry = {"idx": idx, "prompt": item['prompt']}
                st.rerun()
          if item.get("latency_ms") is not None:
            _wc_badge = f'<span style="font-size:11px;color:#888;font-family:monospace">&nbsp;&nbsp;📝 {_words} words · {_chars} chars</span>' if item['response'].strip() else ''
            st.markdown(latency_badge(item["latency_ms"], turn, item.get("timing_details")) + _wc_badge, unsafe_allow_html=True)

          if item['response'].strip():
            current = st.session_state.verdicts.get(idx, "")
            locked = st.session_state.is_processing or st.session_state.is_responding
            lock_tip = (
              "⚠️ Batch is still running — select verdicts once it completes." if st.session_state.is_processing
              else "⚠️ Waiting for response — select verdict once it arrives." if st.session_state.is_responding
              else None
            )
            cols = st.columns(len(_verdict_options))
            for col, opt in zip(cols, _verdict_options):
              clicked = col.button(
                opt,
                key=f"v_{turn}_{opt}",
                type="primary" if current == opt else "secondary",
                use_container_width=True,
                disabled=locked,
                help=lock_tip,
              )
              if clicked:
                if current == opt:
                  st.session_state.verdicts[idx] = ""
                  st.toast(f"Verdict cleared for Turn {turn}", icon="🗑️")
                else:
                  st.session_state.verdicts[idx] = opt
                  st.toast(f"Turn {turn} → {opt}", icon="✅")
                st.rerun()
chat_container = st.container(height=400)
render_history()


if st.session_state.pending_retry:
  _retry = st.session_state.pending_retry
  st.session_state.pending_retry = None
  with st.spinner("Retrying..."):
    _r_resp, _r_lat, _r_tim = call_model(_retry["prompt"], u_id, s_id)
  _ri = _retry["idx"]
  st.session_state.chat_history[_ri]["response"] = _r_resp
  st.session_state.chat_history[_ri]["latency_ms"] = _r_lat
  st.session_state.chat_history[_ri]["timing_details"] = _r_tim
  if _ri < len(st.session_state.results):
    st.session_state.results[_ri]["response"] = _r_resp if _r_resp.strip() else "[BLANK]"
    st.session_state.results[_ri]["latency (s)"] = round(_r_lat / 1000, 2)
    st.session_state.results[_ri]["timing details"] = " | ".join(f"{k}: {v}" for k, v in _r_tim.items() if v is not None) if _r_tim else ""
  st.rerun()

# -------------------------
# 7. Manual Input Logic (UPDATED)
# -------------------------
if prompt := st.chat_input("Message Violet...", disabled=st.session_state.is_processing or st.session_state.is_responding):
  st.session_state.pending_manual_prompt = prompt
  st.session_state.is_responding = True
  st.rerun()

if st.session_state.is_responding and st.session_state.pending_manual_prompt:
  prompt = st.session_state.pending_manual_prompt
  st.session_state.pending_manual_prompt = None
  with st.spinner("Violet is thinking..."):
    response, latency_ms, timing_details = call_model(prompt, u_id, s_id)
  st.session_state.chat_history.append({"source": "manual", "prompt": prompt, "response": response, "latency_ms": latency_ms, "timing_details": timing_details})
  st.session_state.results.append({"User id": u_id, "Session id": s_id, "source": "manual", "prompt": prompt, "response": response if response.strip() else "[BLANK]", "latency (s)": round(latency_ms / 1000, 2), "timing details": " | ".join(f"{k}: {v}" for k, v in timing_details.items() if v is not None) if timing_details else ""})
  st.session_state.is_responding = False
  st.rerun()

# -------------------------
# 8. CSV Batch Logic (UPDATED)
# -------------------------
if start_clicked and uploaded_file is not None:
  st.session_state.is_processing = True
  st.session_state.batch_pending = True
  st.session_state.processing_done = False
  st.rerun()

if st.session_state.batch_pending and uploaded_file is not None:
  st.session_state.batch_pending = False

  row_user_id = st.session_state.generated_user_id
  row_session_id = st.session_state.generated_session_id

  try:
    fname = uploaded_file.name.lower()
    df = pd.read_excel(uploaded_file) if fname.endswith((".xlsx", ".xls")) else pd.read_csv(uploaded_file)
    if prompt_col not in df.columns:
      status_area.error(f"Column '{prompt_col}' not found.")
      st.session_state.is_processing = False
    else:
      prompts = [str(v).strip() for v in df[prompt_col] if str(v).strip()]
      total = len(prompts)
      status_area.info(f"Processing {total} prompts...")

      for idx, p in enumerate(prompts, start=1):



        turn = len(st.session_state.chat_history) + 1

        verdict_idx = turn - 1
        with chat_container:
          with st.chat_message("user", avatar="📄"):
            st.write(p)
          with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Violet is thinking..."):
              resp, latency_ms, timing_details = call_model(p, row_user_id, row_session_id)
            if resp.strip():
              st.write(resp)
            else:
              st.warning("⚠️ No response received")
            st.markdown(latency_badge(latency_ms, turn, timing_details), unsafe_allow_html=True)
            if resp.strip():
              current = st.session_state.verdicts.get(verdict_idx, "")
              cols = st.columns(len(_verdict_options))
              for col, opt in zip(cols, _verdict_options):
                col.button(
                opt,
                key=f"v_{turn}_{opt}",
                type="primary" if current == opt else "secondary",
                use_container_width=True,
                disabled=True,
                help="⚠️ Batch is still running — select verdicts once it completes.",
              )

        time.sleep(0.2)

        st.session_state.results.append({
          "User id": row_user_id,
          "Session id": row_session_id,
          "source": "csv",
          "prompt": p,
          "response": resp if resp.strip() else "[BLANK]",
          "latency (s)": round(latency_ms / 1000, 2),
          "timing details": " | ".join(f"{k}: {v}" for k, v in timing_details.items() if v is not None) if timing_details else "",
        })
        st.session_state.chat_history.append({
          "type": "batch",
          "user_id": row_user_id,
          "session_id": row_session_id,
          "source": "csv",
          "prompt": p,
          "response": resp,
          "latency_ms": latency_ms,
          "timing_details": timing_details,
        })

        progress_bar.progress(int((idx / total) * 100))
        status_area.info(f"Processing: {idx}/{total} | Last: {latency_ms/1000:.2f}s")

      st.session_state.processing_done = True
      st.session_state.is_processing = False
      status_area.success("✅ Batch Complete!")
      st.rerun()

  except Exception as e:
    st.session_state.is_processing = False
    status_area.error(f"Error: {e}")
