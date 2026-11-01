/**
 * ============================================================================
 * EXTRATOR DE CANAIS DO WHATSAPP WEB v3.0 (BRASNAM 2026)
 * ============================================================================
 * Novidades da v3.0:
 * 1. Rolagem Automática Inteligente até uma DATA INICIAL ALVO (ex: 05/10/2026
 *    ou 18/10/2026) configurável direto no painel flutuante!
 * 2. Mostra em tempo real a "Data mais antiga alcançada" conforme sobe a tela.
 * 3. Destrava o carregamento de lotes antigos do WhatsApp Web (simula scroll
 *    no topo + aguarda o spinner do WhatsApp carregar mais histórico).
 * 4. Separa automaticamente as mensagens por Canal para não misturar dois
 *    canais no mesmo arquivo JSON sem querer.
 * ============================================================================
 */

(function () {
  const oldPanel = document.getElementById("brasnam-extractor-panel");
  if (oldPanel) oldPanel.remove();
  if (window.__brasnamScrollTimer) clearInterval(window.__brasnamScrollTimer);

  // Mapa separado por canal: { "EXÉRCITO DO LULA": Map(), "TROPA DO FLÁVIO": Map() }
  window.__brasnamByChannel = window.__brasnamByChannel || {};

  let isAutoScrolling = false;
  let oldestDateReached = null; // Date object da msg mais antiga vista no canal atual
  let oldestDateStr = "Nenhuma ainda";
  let stuckAtTopCounter = 0;
  let lastCountForStuckCheck = 0;

  function getChannelName() {
    const headerEl =
      document.querySelector('#main header span[dir="auto"]') ||
      document.querySelector('header span[dir="auto"]') ||
      document.querySelector('#main header span[title]');
    return headerEl ? headerEl.innerText.trim() : "Canal_Desconhecido";
  }

  function getCurrentChannelMap() {
    const ch = getChannelName();
    if (!window.__brasnamByChannel[ch]) {
      window.__brasnamByChannel[ch] = new Map();
    }
    return window.__brasnamByChannel[ch];
  }

  // Converte "DD/MM/YYYY" (e opcionalmente "HH:MM") em objeto Date
  function parsePtBrDate(dateStr, timeStr = "00:00") {
    if (!dateStr) return null;
    const m = dateStr.trim().match(/^(\d{1,2})\/(\d{1,2})\/(\d{2,4})$/);
    if (!m) return null;
    const day = parseInt(m[1], 10);
    const month = parseInt(m[2], 10) - 1;
    let year = parseInt(m[3], 10);
    if (year < 100) year += 2000;

    let hours = 0,
      mins = 0;
    const tm = (timeStr || "").match(/(\d{1,2}):(\d{2})/);
    if (tm) {
      hours = parseInt(tm[1], 10);
      mins = parseInt(tm[2], 10);
    }
    return new Date(year, month, day, hours, mins, 0);
  }

  function formatPtBrDate(dt) {
    if (!dt) return "—";
    const dd = String(dt.getDate()).padStart(2, "0");
    const mm = String(dt.getMonth() + 1).padStart(2, "0");
    const yyyy = dt.getFullYear();
    const hh = String(dt.getHours()).padStart(2, "0");
    const min = String(dt.getMinutes()).padStart(2, "0");
    return `${dd}/${mm}/${yyyy} ${hh}:${min}`;
  }

  function extractUrls(text) {
    if (!text) return [];
    const urlRegex = /(https?:\/\/[^\s)\]"'>]+)/gi;
    return Array.from(new Set(text.match(urlRegex) || []));
  }

  function extractHashtags(text) {
    if (!text) return [];
    const tagRegex = /(#[a-zA-Z0-9_\u00C0-\u017F]+)/g;
    return Array.from(new Set(text.match(tagRegex) || []));
  }

  function scanVisibleMessages() {
    const channelName = getChannelName();
    const channelMap = getCurrentChannelMap();

    // Seleciona apenas elementos com [data-id] para evitar duplicar pai e filho
    let msgNodes = document.querySelectorAll("#main [data-id]");
    if (msgNodes.length === 0) {
      msgNodes = document.querySelectorAll('#main div[role="row"]');
    }

    msgNodes.forEach((node) => {
      try {
        const dataId =
          node.getAttribute("data-id") ||
          node.querySelector("[data-id]")?.getAttribute("data-id");

        const textEls = node.querySelectorAll(
          '.copyable-text span[dir="ltr"], .copyable-text span[dir="auto"], span.selectable-text'
        );
        let fullText = "";
        if (textEls.length > 0) {
          const parts = [];
          textEls.forEach((el) => {
            if (!el.querySelector(".selectable-text")) {
              parts.push(el.innerText);
            }
          });
          fullText = parts.join("\n").trim();
        } else {
          fullText = node.innerText?.trim() || "";
        }

        const copyableNode = node.querySelector("[data-pre-plain-text]");
        const prePlainText = copyableNode
          ? copyableNode.getAttribute("data-pre-plain-text")
          : "";

        // Extrai data e hora do prePlainText ex: "[17:36, 23/10/2026] EXÉRCITO DO LULA : "
        let msgDateObj = null;
        let dateExtracted = "";
        let timeLabel = "";

        const preMatch = prePlainText.match(
          /\[(\d{1,2}:\d{2}),\s*(\d{1,2}\/\d{1,2}\/\d{2,4})\]/
        );
        if (preMatch) {
          timeLabel = preMatch[1];
          dateExtracted = preMatch[2];
          msgDateObj = parsePtBrDate(dateExtracted, timeLabel);
        } else {
          const timeNodes = node.querySelectorAll(
            'span[dir="auto"], div[role="button"] span'
          );
          timeNodes.forEach((t) => {
            const txt = t.innerText.trim();
            if (/^\d{1,2}:\d{2}(\s?[AP]M)?$/i.test(txt)) {
              timeLabel = txt;
            }
          });
        }

        if (msgDateObj) {
          if (!oldestDateReached || msgDateObj < oldestDateReached) {
            oldestDateReached = msgDateObj;
            oldestDateStr = formatPtBrDate(msgDateObj);
          }
        }

        const anchorLinks = Array.from(node.querySelectorAll("a[href]"))
          .map((a) => a.getAttribute("href"))
          .filter((href) => href && /^https?:\/\//i.test(href));
        const textLinks = extractUrls(fullText);
        const allUrls = Array.from(new Set([...anchorLinks, ...textLinks]));
        const hashtags = extractHashtags(fullText);

        const emojisList = [];
        let reactionTotalRaw = "";
        const reactionButtons = node.querySelectorAll(
          '[aria-label*="reaç"], [aria-label*="reaction"], button[aria-label], div[role="button"]'
        );

        reactionButtons.forEach((btn) => {
          const label = btn.getAttribute("aria-label") || "";
          const inner = btn.innerText?.trim() || "";
          const combined = `${label} ${inner}`;

          const foundEmojis = combined.match(
            /[\p{Emoji_Presentation}\p{Extended_Pictographic}]/gu
          );
          if (foundEmojis && foundEmojis.length > 0) {
            foundEmojis.forEach((em) => {
              if (!emojisList.includes(em)) emojisList.push(em);
            });
            const countMatch = combined.match(
              /\b(\d+(?:[.,]\d+)?\s*(?:mil|mi|k|m)?)\b/i
            );
            if (countMatch && !/^\d{1,2}:\d{2}$/.test(countMatch[1])) {
              reactionTotalRaw = countMatch[1].trim();
            }
          }
        });

        const hasVideo = !!node.querySelector(
          "video, [data-icon*='video'], [aria-label*='vídeo'], [aria-label*='video']"
        );
        const hasImage = !!node.querySelector(
          "img[src*='blob:'], img[src*='mmg.whatsapp.net']"
        );
        const hasAudio = !!node.querySelector(
          "audio, [data-icon*='audio'], [data-icon*='ptt']"
        );

        if (!fullText && allUrls.length === 0 && !hasVideo && !hasImage) {
          return;
        }

        const uniqueKey =
          dataId ||
          `${channelName}_${prePlainText}_${timeLabel}_${fullText.slice(0, 120)}`;

        const reactionsCompat = {};
        emojisList.forEach((e) => (reactionsCompat[e] = reactionTotalRaw || ","));

        channelMap.set(uniqueKey, {
          id: uniqueKey,
          channel_name: channelName,
          captured_at_iso: new Date().toISOString(),
          pre_plain_text: prePlainText,
          date_str: dateExtracted,
          time_label: timeLabel,
          text: fullText,
          urls: allUrls,
          hashtags: hashtags,
          top_emojis: emojisList,
          reaction_total_raw: reactionTotalRaw,
          reactions: reactionsCompat,
          media: {
            has_video: hasVideo,
            has_image: hasImage,
            has_audio: hasAudio,
          },
        });
      } catch (err) {}
    });

    updateFloatingUI();
  }

  // Encontra o container rolável real da conversa no WhatsApp Web
  function getScrollContainer() {
    const main = document.querySelector("#main");
    if (!main) return null;

    // 1. Procura pela div que envolve role="application" ou role="region"
    const appRole = main.querySelector('[role="application"], [role="region"]');
    if (appRole) {
      let el = appRole;
      while (el && el !== main) {
        const style = window.getComputedStyle(el);
        if (
          (style.overflowY === "auto" || style.overflowY === "scroll") &&
          el.scrollHeight > el.clientHeight
        ) {
          return el;
        }
        el = el.parentElement;
      }
    }

    // 2. Fallback: busca a div com maior scrollHeight dentro de #main
    let bestDiv = null;
    let maxScroll = 0;
    main.querySelectorAll("div").forEach((div) => {
      const style = window.getComputedStyle(div);
      if (
        (style.overflowY === "auto" || style.overflowY === "scroll") &&
        div.scrollHeight > div.clientHeight + 20
      ) {
        if (div.scrollHeight > maxScroll) {
          maxScroll = div.scrollHeight;
          bestDiv = div;
        }
      }
    });
    return bestDiv;
  }

  function getTargetStartDate() {
    const input = document.getElementById("brasnam-target-date");
    const raw = input ? input.value.trim() : "05/10/2026";
    return parsePtBrDate(raw, "00:00");
  }

  function stopAutoScroll(reasonMsg) {
    isAutoScrolling = false;
    if (window.__brasnamScrollTimer) {
      clearInterval(window.__brasnamScrollTimer);
      window.__brasnamScrollTimer = null;
    }
    updateFloatingUI();
    if (reasonMsg) {
      const statusEl = document.getElementById("brasnam-status-msg");
      if (statusEl) {
        statusEl.innerText = reasonMsg;
        statusEl.style.color = "#00a884";
      }
      console.log("🏁 " + reasonMsg);
    }
  }

  function toggleAutoScroll() {
    if (isAutoScrolling) {
      stopAutoScroll("⏸️ Rolagem pausada pelo usuário.");
      return;
    }

    isAutoScrolling = true;
    stuckAtTopCounter = 0;
    lastCountForStuckCheck = getCurrentChannelMap().size;
    updateFloatingUI();

    const statusEl = document.getElementById("brasnam-status-msg");
    if (statusEl) {
      statusEl.innerText = "⏳ Subindo histórico até a data inicial...";
      statusEl.style.color = "#f7b928";
    }

    window.__brasnamScrollTimer = setInterval(() => {
      scanVisibleMessages();

      // Verifica se já alcançou a data inicial desejada
      const targetDate = getTargetStartDate();
      if (targetDate && oldestDateReached && oldestDateReached <= targetDate) {
        stopAutoScroll(
          `✅ Meta atingida! Chegou em ${oldestDateStr}. Clique em Baixar JSON!`
        );
        return;
      }

      const container = getScrollContainer();
      if (!container) return;

      // Rola para cima
      container.scrollBy({ top: -900, behavior: "auto" });

      // Dispara evento de Wheel para forçar o WhatsApp Web a carregar mais mensagens quando encosta no topo
      if (container.scrollTop <= 15) {
        container.scrollTop = 10;
        container.dispatchEvent(
          new WheelEvent("wheel", { deltaY: -800, bubbles: true })
        );
        setTimeout(() => {
          if (container) container.scrollTop = 0;
        }, 250);
      }

      // Verifica se chegou ao início absoluto do canal (sem novas mensagens por várias iterações no topo)
      const currentSize = getCurrentChannelMap().size;
      if (currentSize === lastCountForStuckCheck && container.scrollTop <= 5) {
        stuckAtTopCounter++;
        if (stuckAtTopCounter >= 12) {
          stopAutoScroll(
            `🏁 Fim do histórico disponível no WhatsApp alcançado (${oldestDateStr})!`
          );
        }
      } else {
        stuckAtTopCounter = 0;
        lastCountForStuckCheck = currentSize;
      }
    }, 950);
  }

  function downloadJSON() {
    scanVisibleMessages();
    const chRaw = getChannelName();
    const channelMap = getCurrentChannelMap();
    const channelSlug = chRaw.replace(/[^\w\d_-]+/g, "_").toLowerCase();

    const payload = {
      metadata: {
        channel_name: chRaw,
        exported_at: new Date().toISOString(),
        oldest_message_reached: oldestDateStr,
        total_messages: channelMap.size,
        source_url: window.location.href,
      },
      messages: Array.from(channelMap.values()),
    };

    const blob = new Blob([JSON.stringify(payload, null, 2)], {
      type: "application/json;charset=utf-8",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `whatsapp_channel_${channelSlug}_${new Date()
      .toISOString()
      .slice(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  const panel = document.createElement("div");
  panel.id = "brasnam-extractor-panel";
  panel.style.cssText = `
    position: fixed;
    top: 16px;
    right: 16px;
    z-index: 999999;
    background: #111b21;
    color: #e9edef;
    border: 2px solid #00a884;
    border-radius: 10px;
    padding: 12px 16px;
    font-family: system-ui, -apple-system, sans-serif;
    font-size: 13px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.55);
    min-width: 300px;
  `;

  panel.innerHTML = `
    <div style="font-weight:700; color:#00a884; margin-bottom:6px; font-size:14px;">
      📊 Coletor BRASNAM 2026 (v3.0 Auto-Date)
    </div>
    <div id="brasnam-channel-label" style="margin-bottom:4px; color:#8696a0;">
      Canal: <strong>Detectando...</strong>
    </div>
    <div id="brasnam-count-label" style="margin-bottom:6px; font-size:14px; font-weight:600;">
      Posts: 0 | Links: 0 | #Tags: 0
    </div>
    <div id="brasnam-oldest-label" style="margin-bottom:8px; font-size:12px; color:#53bdeb;">
      📅 Mais antiga lida: <strong>—</strong>
    </div>
    <div style="margin-bottom:10px; display:flex; align-items:center; gap:6px;">
      <label style="font-size:12px; color:#8696a0;">Rolar até data:</label>
      <input id="brasnam-target-date" type="text" value="05/10/2026"
        style="background:#202c33; color:#fff; border:1px solid #3b4a54; border-radius:4px; padding:3px 6px; width:95px; font-size:12px; text-align:center;"
        title="Digite DD/MM/AAAA (ex: 05/10/2026 para início do 2º turno ou 18/10/2026 para última semana)" />
    </div>
    <div id="brasnam-status-msg" style="margin-bottom:8px; font-size:11.5px; color:#8696a0;">
      Pronto para iniciar coleta.
    </div>
    <div style="display:flex; gap:8px; flex-wrap:wrap;">
      <button id="brasnam-btn-scroll" style="background:#00a884; color:#111b21; border:none; padding:6px 10px; border-radius:6px; font-weight:700; cursor:pointer;">
        ▶️ Rolar até Data Inicial
      </button>
      <button id="brasnam-btn-save" style="background:#202c33; color:#e9edef; border:1px solid #00a884; padding:6px 10px; border-radius:6px; font-weight:600; cursor:pointer;">
        💾 Baixar JSON
      </button>
      <button id="brasnam-btn-clear" style="background:#2a3942; color:#f15c6d; border:none; padding:6px 8px; border-radius:6px; cursor:pointer;" title="Zerar canal atual">
        🗑️
      </button>
    </div>
  `;

  document.body.appendChild(panel);

  function updateFloatingUI() {
    const chLabel = document.getElementById("brasnam-channel-label");
    const cntLabel = document.getElementById("brasnam-count-label");
    const oldLabel = document.getElementById("brasnam-oldest-label");
    const btnScroll = document.getElementById("brasnam-btn-scroll");

    const channelMap = getCurrentChannelMap();
    let totalUrls = 0;
    let totalTags = 0;
    channelMap.forEach((m) => {
      totalUrls += m.urls.length;
      totalTags += (m.hashtags || []).length;
    });

    if (chLabel) {
      chLabel.innerHTML = `Canal: <strong style="color:#fff">${getChannelName()}</strong>`;
    }
    if (cntLabel) {
      cntLabel.innerHTML = `Posts: <span style="color:#00a884">${channelMap.size}</span> | Links: <span style="color:#53bdeb">${totalUrls}</span> | #Tags: <span style="color:#f7b928">${totalTags}</span>`;
    }
    if (oldLabel) {
      oldLabel.innerHTML = `📅 Mais antiga lida: <strong style="color:#fff">${oldestDateStr}</strong>`;
    }
    if (btnScroll) {
      btnScroll.innerText = isAutoScrolling
        ? "⏸️ Pausar Scroll"
        : "▶️ Rolar até Data Inicial";
      btnScroll.style.background = isAutoScrolling ? "#f15c6d" : "#00a884";
    }
  }

  document
    .getElementById("brasnam-btn-scroll")
    .addEventListener("click", toggleAutoScroll);
  document
    .getElementById("brasnam-btn-save")
    .addEventListener("click", downloadJSON);
  document.getElementById("brasnam-btn-clear").addEventListener("click", () => {
    const ch = getChannelName();
    if (confirm(`Limpar mensagens acumuladas do canal "${ch}"?`)) {
      getCurrentChannelMap().clear();
      oldestDateReached = null;
      oldestDateStr = "Nenhuma ainda";
      updateFloatingUI();
    }
  });

  window.addEventListener("scroll", () => scanVisibleMessages(), true);
  scanVisibleMessages();
  console.log("✅ Coletor BRASNAM 2026 v3.0 (Auto-Date) carregado!");
})();
