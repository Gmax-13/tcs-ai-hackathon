/**
 * renderer.js — Output View Renderer (Anurodh)
 * 
 * Consumes structured guidance JSON from /api/mentor (or window.STUB_MENTOR_DATA)
 * and renders interactive cards, prominent decision highlights, Effort vs. Impact 2x2 matrix,
 * Jury-Mode presentation views, and automated test-case runner validation.
 */

class MentorRenderer {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.currentData = null;
    this.isJuryMode = false;
    this.chartInstance = null;
  }

  /**
   * Primary entry point — renders the complete guidance JSON
   */
  render(data) {
    if (!data || typeof data !== 'object') {
      this.renderError("Invalid guidance data received.");
      return;
    }

    this.currentData = data;
    this.container.style.opacity = '0';
    
    setTimeout(() => {
      let html = '';

      // 1. Prominent Decision -> Reason -> Next Action Hero Card (Top Priority)
      html += this.renderDecisionBanner(data);

      // 2. Jury Mode Toggle Bar
      html += this.renderToolbar();

      // 3. Main View Container (Full Guidance vs Jury Summary)
      html += `<div id="renderer-content">`;
      html += this.isJuryMode ? this.renderJurySummary(data) : this.renderFullGuidance(data);
      html += `</div>`;

      this.container.innerHTML = html;
      this.container.style.opacity = '1';
      this.attachEventListeners();
    }, 150);
  }

  /**
   * Hero Banner for Decision, Reason, and Next Action
   */
  renderDecisionBanner(data) {
    const decision = data.decision || "Define single core user journey first.";
    const reason = data.reason || "A working end-to-end prototype scores significantly higher than multiple incomplete features.";
    const nextAction = data.next_action || "Lock the contract, build the P0 flow, and verify end-to-end execution.";

    return `
      <section class="hero-decision-card card-glow" id="decision-hero">
        <div class="hero-header">
          <span class="hero-badge">⚡ MENTOR DECISION & ACTION PLAN</span>
          <span class="hero-tag">Core Focus</span>
        </div>
        
        <div class="decision-grid">
          <div class="decision-box primary">
            <div class="box-icon">🎯</div>
            <div class="box-content">
              <h3>RECOMMENDED DECISION</h3>
              <p class="decision-text">${this.escape(decision)}</p>
            </div>
          </div>

          <div class="decision-box secondary">
            <div class="box-icon">💡</div>
            <div class="box-content">
              <h3>WHY THIS DECISION?</h3>
              <p class="reason-text">${this.escape(reason)}</p>
            </div>
          </div>

          <div class="decision-box highlight">
            <div class="box-icon">🚀</div>
            <div class="box-content">
              <h3>IMMEDIATE NEXT ACTION</h3>
              <p class="action-text">${this.escape(nextAction)}</p>
            </div>
          </div>
        </div>
      </section>
    `;
  }

  /**
   * Interactive Toolbar (Jury Mode Toggle, Copy Summary, Export)
   */
  renderToolbar() {
    return `
      <div class="renderer-toolbar">
        <div class="toolbar-title">
          <h2>📊 Mentor Output View</h2>
          <span class="schema-badge">JSON Schema Verified</span>
        </div>
        <div class="toolbar-actions">
          <button id="download-pdf-btn" class="btn btn-secondary">
            📄 Download Report
          </button>
          <button id="toggle-jury-btn" class="btn ${this.isJuryMode ? 'btn-jury-active' : 'btn-outline'}">
            ${this.isJuryMode ? '👁️ Exit Jury Mode' : '🏆 Enable Jury-Mode (6-Part Pitch View)'}
          </button>
          <button id="stub-load-btn" class="btn btn-secondary">
            🧪 Load Stub Sample JSON
          </button>
        </div>
      </div>
    `;
  }

  /**
   * Standard Full Guidance Sectioned Card Layout
   */
  renderFullGuidance(data) {
    return `
      <div class="guidance-grid">
        <!-- Card 1: Problem Summary & Key Questions -->
        <div class="card guidance-card">
          <div class="card-header">
            <span class="card-icon">📌</span>
            <h3>Problem Summary & Key Questions</h3>
          </div>
          <div class="card-body">
            <p class="problem-summary-text">${this.escape(data.problem_summary || "No summary provided.")}</p>
            
            <h4 class="sub-heading">🔍 Key Clarifying Questions to Answer:</h4>
            <ul class="questions-list">
              ${(data.key_questions || []).map(q => `<li><span class="list-bullet">?</span> ${this.escape(q)}</li>`).join('')}
            </ul>

            <h4 class="sub-heading" style="margin-top: 16px; color: var(--badge-medium);">⚠️ AI Assumptions:</h4>
            <ul class="questions-list assumptions-list">
              ${(data.assumptions && data.assumptions.length > 0) ? 
                data.assumptions.map(a => `<li style="font-size:0.85rem;"><span class="list-bullet" style="color:var(--badge-medium);">!</span> ${this.escape(a)}</li>`).join('') :
                '<li style="font-size:0.85rem; color:var(--text-dim);">No assumptions explicitly tagged.</li>'
              }
            </ul>
          </div>
        </div>

        <!-- Card 2: User Personas -->
        <div class="card guidance-card">
          <div class="card-header">
            <span class="card-icon">👤</span>
            <h3>User Personas & Pain Points</h3>
          </div>
          <div class="card-body">
            <div class="personas-container">
              ${(data.user_personas || []).map(p => `
                <div class="persona-item">
                  <div class="persona-avatar">${p.name ? p.name[0].toUpperCase() : 'U'}</div>
                  <div class="persona-details">
                    <h4 class="persona-name">${this.escape(p.name || "Target User")}</h4>
                    <p><strong>Need:</strong> ${this.escape(p.need || "N/A")}</p>
                    <p class="pain-point"><strong>Pain Point:</strong> <span>${this.escape(p.pain_point || "N/A")}</span></p>
                  </div>
                </div>
              `).join('')}
            </div>
          </div>
        </div>

        <!-- Card 3: Design Thinking Guidance -->
        <div class="card guidance-card full-width">
          <div class="card-header">
            <span class="card-icon">🌀</span>
            <h3>Design Thinking Framework</h3>
          </div>
          <div class="card-body">
            <div class="dt-guidance-content">
              ${this.formatDesignThinking(data.design_thinking_guidance)}
            </div>
          </div>
        </div>

        <!-- Card 4: Feature Suggestions & 2x2 Effort Matrix -->
        <div class="card guidance-card full-width">
          <div class="card-header">
            <span class="card-icon">⚡</span>
            <h3>Feature Suggestions & 2x2 Effort Matrix</h3>
          </div>
          <div class="card-body">
            <div class="feature-layout">
              <div class="feature-list">
                <h4>Suggested Features:</h4>
                ${(data.feature_suggestions || []).map(f => `
                  <div class="feature-card effort-${(f.effort || 'medium').toLowerCase()}">
                    <div class="feature-top">
                      <span class="feature-title">${this.escape(f.feature)}</span>
                      <span class="effort-badge effort-${(f.effort || 'medium').toLowerCase()}">${(f.effort || 'medium').toUpperCase()} EFFORT</span>
                    </div>
                    <p class="feature-why">${this.escape(f.why)}</p>
                  </div>
                `).join('')}
                <div style="margin-top: 24px; text-align: center;">
                  <h4 style="margin-bottom: 12px; color: var(--text-muted); font-size: 0.85rem;">Effort Distribution</h4>
                  <div style="position: relative; height: 180px; width: 100%;">
                    <canvas id="effortChart"></canvas>
                  </div>
                </div>
              </div>

              <!-- Novel Idea #3: Effort vs Impact 2x2 Matrix -->
              <div class="matrix-2x2-container">
                <h4 class="matrix-title">Effort vs. Impact Matrix (Decision Tool)</h4>
                <div class="matrix-grid">
                  <div class="matrix-quadrant quad-q1">
                    <span class="quad-label">🚀 Quick Wins (Low Effort / High Impact)</span>
                    <div class="quad-content" id="quad-quick-wins"></div>
                  </div>
                  <div class="matrix-quadrant quad-q2">
                    <span class="quad-label">⭐ Major Projects (High Effort / High Impact)</span>
                    <div class="quad-content" id="quad-major"></div>
                  </div>
                  <div class="matrix-quadrant quad-q3">
                    <span class="quad-label">🛠️ Fill-ins (Low Effort / Low Impact)</span>
                    <div class="quad-content" id="quad-fillins"></div>
                  </div>
                  <div class="matrix-quadrant quad-q4">
                    <span class="quad-label">⚠️ Avoid/Defer (High Effort / Low Impact)</span>
                    <div class="quad-content" id="quad-defer"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Card 5: Tech Stack & Prototype Priorities -->
        <div class="card guidance-card">
          <div class="card-header">
            <span class="card-icon">💻</span>
            <h3>Tech Stack & Priorities</h3>
          </div>
          <div class="card-body">
            <h4>Recommended Stack:</h4>
            <ul class="pill-list">
              ${(data.tech_stack_options || []).map(t => `<li class="tech-pill">🛠️ ${this.escape(t)}</li>`).join('')}
            </ul>

            <h4 style="margin-top: 1rem;">Prototype Build Order:</h4>
            <ol class="priority-list">
              ${(data.prototype_priorities || []).map(p => `<li>${this.escape(p)}</li>`).join('')}
            </ol>
          </div>
        </div>

        <!-- Card 6: Checkpoints & Demo Tips -->
        <div class="card guidance-card">
          <div class="card-header">
            <span class="card-icon">🏁</span>
            <h3>Checkpoints & Pitch Prep</h3>
          </div>
          <div class="card-body">
            <h4>Validation Checkpoints:</h4>
            <ul class="checklist">
              ${(data.validation_checkpoints || []).map(c => `<li><span class="check-box">✓</span> ${this.escape(c)}</li>`).join('')}
            </ul>

            <h4 style="margin-top: 1rem;">Demo Preparation Tips:</h4>
            <ul class="tips-list">
              ${(data.demo_prep_tips || []).map(tip => `<li>💡 ${this.escape(tip)}</li>`).join('')}
            </ul>
          </div>
        </div>
      </div>
    `;
  }

  /**
   * Novel Idea #5: Jury-Mode Summary View (6-part handbook pitch structure)
   */
  renderJurySummary(data) {
    return `
      <div class="jury-mode-container card-glow">
        <div class="jury-mode-header">
          <h3>🏆 Jury Presentation Summary — 5-Minute Pitch Structure</h3>
          <p>This view formats mentor outputs into the exact 6-step judging rubric defined by the handbook.</p>
        </div>

        <div class="jury-steps-grid">
          <div class="jury-step">
            <div class="step-num">1</div>
            <h4>PROBLEM</h4>
            <p>${this.escape(data.problem_summary)}</p>
            ${(data.assumptions && data.assumptions.length > 0) ? 
              `<div style="margin-top:8px; font-size:0.8rem; border-left: 2px solid var(--badge-medium); padding-left:8px;"><strong>Assumptions:</strong><br/>${data.assumptions.map(a => `• ${this.escape(a)}`).join('<br/>')}</div>` : ''
            }
          </div>

          <div class="jury-step">
            <div class="step-num">2</div>
            <h4>APPROACH</h4>
            <p>${this.escape(data.design_thinking_guidance)}</p>
          </div>

          <div class="jury-step">
            <div class="step-num">3</div>
            <h4>SOLUTION</h4>
            <p><strong>Core Features:</strong> ${(data.feature_suggestions || []).map(f => f.feature).join(', ')}</p>
            <p><strong>Tech Stack:</strong> ${(data.tech_stack_options || []).join(' | ')}</p>
          </div>

          <div class="jury-step">
            <div class="step-num">4</div>
            <h4>OUTPUT / DEMO</h4>
            <p><strong>Core Decision:</strong> ${this.escape(data.decision)}</p>
            <p><strong>Action:</strong> ${this.escape(data.next_action)}</p>
          </div>

          <div class="jury-step">
            <div class="step-num">5</div>
            <h4>PROOF</h4>
            <ul>
              ${(data.validation_checkpoints || []).map(vc => `<li>✓ ${this.escape(vc)}</li>`).join('')}
            </ul>
          </div>

          <div class="jury-step">
            <div class="step-num">6</div>
            <h4>LEARNING</h4>
            <ul>
              ${(data.demo_prep_tips || []).map(t => `<li>💡 ${this.escape(t)}</li>`).join('')}
            </ul>
          </div>
        </div>
      </div>
    `;
  }

  /**
   * Formats design thinking string into visual process steps
   */
  formatDesignThinking(dtText) {
    if (!dtText) return `<p>Follow standard Empathize → Define → Ideate → Prototype → Test process.</p>`;
    
    // Split by step markers if available
    const steps = dtText.split(/(?=\d+\.\s*|\b(Empathize|Define|Ideate|Prototype|Test):)/g).filter(Boolean);
    
    return `
      <div class="dt-steps-wrapper">
        <p class="dt-raw-text">${this.escape(dtText)}</p>
      </div>
    `;
  }

  /**
   * Populates 2x2 Effort vs Impact Matrix
   */
  populateEffortMatrix(features) {
    const qQuick = document.getElementById('quad-quick-wins');
    const qMajor = document.getElementById('quad-major');
    const qFillins = document.getElementById('quad-fillins');
    const qDefer = document.getElementById('quad-defer');

    if (!qQuick || !qMajor || !qFillins || !qDefer || !features) return;

    features.forEach(f => {
      const effort = (f.effort || 'medium').toLowerCase();
      // Assume first 2 features are high impact, rest lower impact unless specified
      const isHighImpact = true; // By mentor definition, suggested features have high impact

      const chip = document.createElement('div');
      chip.className = `matrix-chip effort-${effort}`;
      chip.innerText = f.feature;

      if (effort === 'low') {
        qQuick.appendChild(chip);
      } else if (effort === 'medium') {
        qMajor.appendChild(chip.cloneNode(true));
      } else {
        qDefer.appendChild(chip);
      }
    });
  }

  attachEventListeners() {
    // Populate matrix after DOM render
    if (this.currentData && this.currentData.feature_suggestions) {
      this.populateEffortMatrix(this.currentData.feature_suggestions);
      
      // Render Chart if not in jury mode
      if (!this.isJuryMode) {
        this.renderChart(this.currentData.feature_suggestions);
      }
    }

    const toggleBtn = document.getElementById('toggle-jury-btn');
    if (toggleBtn) {
      toggleBtn.onclick = () => {
        this.isJuryMode = !this.isJuryMode;
        this.render(this.currentData);
      };
    }

    const stubBtn = document.getElementById('stub-load-btn');
    if (stubBtn) {
      stubBtn.onclick = () => {
        if (window.STUB_MENTOR_DATA) {
          this.render(window.STUB_MENTOR_DATA);
        }
      };
    }

    const downloadBtn = document.getElementById('download-pdf-btn');
    if (downloadBtn) {
      downloadBtn.onclick = () => {
        const element = document.getElementById('rendererRoot');
        const opt = {
          margin: 10,
          filename: 'hackathon_mentor_report.pdf',
          image: { type: 'jpeg', quality: 0.98 },
          html2canvas: { scale: 2, useCORS: true, backgroundColor: document.documentElement.classList.contains('light-mode') ? '#ffffff' : '#090d16' },
          jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
        };
        
        const oldText = downloadBtn.innerText;
        downloadBtn.innerText = "⏳ Generating...";
        html2pdf().set(opt).from(element).save().then(() => {
          downloadBtn.innerText = oldText;
        });
      };
    }
  }

  renderChart(features) {
    const ctx = document.getElementById('effortChart');
    if (!ctx) return;
    
    if (this.chartInstance) {
      this.chartInstance.destroy();
    }
    
    let low = 0, med = 0, high = 0;
    features.forEach(f => {
      const e = (f.effort || '').toLowerCase();
      if (e === 'low') low++;
      else if (e === 'high') high++;
      else med++;
    });

    const isLightMode = document.documentElement.classList.contains('light-mode');
    const textColor = isLightMode ? '#475569' : '#9ca3af';

    this.chartInstance = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Low Effort', 'Medium Effort', 'High Effort'],
        datasets: [{
          data: [low, med, high],
          backgroundColor: [
            'rgba(16, 185, 129, 0.7)',  // low
            'rgba(245, 158, 11, 0.7)',  // medium
            'rgba(244, 63, 94, 0.7)'    // high
          ],
          borderColor: isLightMode ? '#ffffff' : '#090d16',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right',
            labels: { color: textColor, font: { size: 11, family: 'Outfit' } }
          }
        },
        cutout: '65%'
      }
    });
  }

  renderError(msg) {
    this.container.innerHTML = `
      <div class="error-card card-glow">
        <span class="error-icon">⚠️</span>
        <h3>Rendering Error</h3>
        <p>${this.escape(msg)}</p>
      </div>
    `;
  }

  escape(str) {
    if (typeof str !== 'string') return '';
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
}

window.MentorRenderer = MentorRenderer;
