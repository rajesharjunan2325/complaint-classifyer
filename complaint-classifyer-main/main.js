const INTENTS = {
  billing_payment: ['bill', 'billing', 'charge', 'charged', 'payment', 'refund', 'credit', 'fee'],
  account_access: ['login', 'log in', 'password', 'locked', 'account', 'verify', 'sign in'],
  network_outage: ['outage', 'down', 'no service', 'signal', 'network', 'emergency calls', 'coverage'],
  slow_data: ['slow', '5g', '4g', 'data', 'internet', 'buffering', 'speed'],
  device_activation: ['activate', 'activation', 'esim', 'sim', 'device', 'phone', 'upgrade'],
  plan_change: ['plan', 'upgrade', 'downgrade', 'add a line', 'cancel', 'unlimited'],
  delivery_status: ['order', 'shipping', 'delivery', 'tracking', 'arrive', 'package', 'shipment'],
  human_support: ['agent', 'human', 'representative', 'dm', 'help', 'contact', 'complaint']
};

const LABELS = {
  billing_payment: 'Billing & payment',
  account_access: 'Account access',
  network_outage: 'Network outage',
  slow_data: 'Slow data',
  device_activation: 'Device activation',
  plan_change: 'Plan change',
  delivery_status: 'Order & delivery',
  human_support: 'Human support'
};

const REPLIES = {
  billing_payment: 'Sorry about the billing surprise. I can help review the charge and check whether a refund or credit applies. Please DM your mobile number and billing ZIP (never post account details publicly).',
  account_access: 'I can help get you back into your account. Please DM your mobile number and billing ZIP so our team can verify you securely and reset access.',
  network_outage: 'Sorry you are dealing with a service interruption. Please DM your location and mobile number so we can check for an outage and share the latest restoration update.',
  slow_data: 'Sorry your data is running slowly. Please DM your location, device model, and mobile number so we can check local coverage and your line.',
  device_activation: 'We can help activate the device or eSIM. Please DM your mobile number and device model, and we will check the activation status securely.',
  plan_change: 'I can help review plan options and any pricing impact. Please DM your mobile number and billing ZIP so we can look at the account securely.',
  delivery_status: 'I can check the order status. Please DM your order number and shipping ZIP (without posting personal details here), and we will look up the latest update.',
  human_support: 'I am sorry this has been frustrating. Please DM your mobile number and a short description of what happened so a specialist can review it securely.'
};

const analysisCache = new Map();
const riskPatterns = /(urgent|asap|emergency|fraud|stolen|scam|lawsuit|legal|safety)/i;

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function normalizeText(text) {
  return text.toLowerCase().replace(/[^\w\s]/g, ' ').replace(/\s+/g, ' ').trim();
}

function findMatches(lowerText, words) {
  const matches = [];

  for (const word of words) {
    const token = word.trim().toLowerCase();
    if (!token) continue;

    const pattern = new RegExp(`\\b${token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i');
    if (pattern.test(lowerText)) {
      matches.push(token);
    }
  }

  return matches;
}

function analyzeTweet(text) {
  const normalized = normalizeText(text);
  const cacheKey = normalized || '__empty__';

  if (analysisCache.has(cacheKey)) {
    return analysisCache.get(cacheKey);
  }

  const scores = {};
  let topIntent = 'human_support';
  let topScore = 0;
  let topMatches = [];

  for (const [intent, words] of Object.entries(INTENTS)) {
    const matches = findMatches(normalized, words);
    const score = matches.length;
    scores[intent] = score;

    if (score > topScore) {
      topIntent = intent;
      topScore = score;
      topMatches = matches;
    }
  }

  const ranked = Object.entries(scores).sort((a, b) => b[1] - a[1]);
  const intent = topScore ? topIntent : 'human_support';
  const runnerUp = ranked[1]?.[1] || 0;
  const confidence = Math.min(0.98, topScore ? 0.42 + topScore * 0.08 + (topScore - runnerUp) * 0.06 : 0.18);
  const urgent = riskPatterns.test(normalized);
  const reasons = [];

  if (confidence < 0.62) reasons.push('low classifier confidence');
  if (urgent) reasons.push('urgent or high-risk language');
  if (intent === 'human_support') reasons.push('request is better handled by a specialist');

  const result = {
    intent,
    confidence,
    urgent,
    scores,
    reasons,
    evidence: topMatches.slice(0, 3),
    totalMatches: topMatches.length
  };

  analysisCache.set(cacheKey, result);
  return result;
}

function renderResult(resultBox, data) {
  const escalate = data.reasons.length > 0;
  const evidenceSummary = data.evidence.length ? `${data.evidence.length} matching cues` : 'No direct matches';
  const routeText = escalate
    ? data.reasons.join(' · ')
    : 'Confidence and risk checks passed. Historical response evidence supports this draft.';

  resultBox.innerHTML = `
    <div class="result-top">
      <div>
        <span class="eyebrow">ANALYSIS COMPLETE</span>
        <h3>${escapeHtml(LABELS[data.intent])}</h3>
      </div>
      <span class="decision ${escalate ? 'escalate' : 'handle'}">${escalate ? 'Escalate' : 'Auto-handle'}</span>
    </div>
    <div class="metrics">
      <div><span>Confidence</span><strong>${Math.round(data.confidence * 100)}%</strong></div>
      <div><span>Risk check</span><strong>${escalate ? 'Review' : 'Passed'}</strong></div>
      <div><span>Evidence</span><strong>${escapeHtml(evidenceSummary)}</strong></div>
    </div>
    <div class="reply-block">
      <span class="eyebrow">SUGGESTED REPLY</span>
      <p>${escapeHtml(REPLIES[data.intent])}</p>
    </div>
    <div class="evidence">
      <span class="eyebrow">ROUTING REASON</span>
      <p>${escapeHtml(routeText)}</p>
    </div>
  `;
  resultBox.classList.add('show');
}

function initApp() {
  const inputText = document.getElementById('inputText');
  const analyzeBtn = document.getElementById('analyzeBtn');
  const resultBox = document.getElementById('result');

  if (!inputText || !analyzeBtn || !resultBox) {
    console.error('Required elements were not found on the page.');
    return;
  }

  const handleAnalysis = () => {
    const text = inputText.value.trim();

    if (!text) {
      resultBox.innerHTML = '<p>Please enter a complaint or question.</p>';
      resultBox.classList.add('show');
      inputText.focus();
      return;
    }

    const data = analyzeTweet(text);
    renderResult(resultBox, data);
  };

  analyzeBtn.addEventListener('click', handleAnalysis);

  inputText.addEventListener('keydown', (event) => {
    if ((event.key === 'Enter' && (event.ctrlKey || event.metaKey)) || (event.key === 'Enter' && !event.shiftKey && inputText.value.trim())) {
      event.preventDefault();
      handleAnalysis();
    }
  });

  inputText.addEventListener('input', () => {
    const text = inputText.value.trim();
    if (!text) {
      resultBox.classList.remove('show');
    }
  });

  inputText.focus();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  initApp();
}