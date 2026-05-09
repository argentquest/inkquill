/* global React */
const { useState } = React;

/**
 * CareCircleFamilyHome — the redesigned Care Circle Family home, as a
 * reusable component so it can be embedded at any width inside a design
 * canvas artboard (desktop / tablet / phone).
 *
 * The CSS lives inline in the host page (Friends World.html) under a
 * `.ccfh` namespace so it doesn't collide with any existing kit styles.
 *
 * Props:
 *   variant — "desktop" | "tablet" | "phone"
 *             Drives the responsive grid breakpoints; the artboard width
 *             does the rest via the same media queries you'd see in prod.
 */

function ProvBadge({ kind = "auto", children }) {
  const glyph = kind === "family"
    ? <path d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.65A4 4 0 0 1 19 10c0 5.5-7 10-7 10z" />
    : kind === "curated"
      ? <g><path d="M3 5h7a2 2 0 0 1 2 2v13" /><path d="M21 5h-7a2 2 0 0 0-2 2v13" /><path d="M3 5v14h18V5" /></g>
      : <g><path d="M12 4v2M12 18v2M4 12h2M18 12h2" /><circle cx="12" cy="12" r="3" /></g>;
  return (
    <span className={`ccfh-prov ccfh-prov--${kind}`}>
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">{glyph}</svg>
      {children}
    </span>
  );
}

function NavCard({ accent, icon, count, suffix, title, sub, arrow, members }) {
  return (
    <a href="#" className={`ccfh-nav ${accent ? "ccfh-nav--accent" : ""}`}>
      <div className="ccfh-nav__row">
        <span className="ccfh-nav__icon">{icon}</span>
        {count && <span className="ccfh-nav__count"><strong>{count}</strong>{suffix}</span>}
      </div>
      <h4 className="ccfh-nav__h">{title}</h4>
      <p className="ccfh-nav__sub">{sub}</p>
      {members && <div className="ccfh-members">{members}</div>}
      {arrow && <span className="ccfh-nav__arrow">{arrow}</span>}
    </a>
  );
}

function CareCircleFamilyHome({ variant = "desktop" }) {
  return (
    <div className={`ccfh ccfh--${variant}`}>
      {/* App chrome */}
      <div className="ccfh-appbar">
        <div className="ccfh-appbar__brand">
          <svg className="ccfh-appbar__mark" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"><path d="M12 3l3 6 6 1-4.5 4.2L18 21l-6-3.5L6 21l1.5-6.8L3 10l6-1z" /></svg>
          Ink &amp; Quill
        </div>
        <div className="ccfh-appbar__right">
          <button className="ccfh-pill ccfh-pill--dark">1,501 Coins</button>
          {variant !== "phone" && <button className="ccfh-pill">Night Mode</button>}
          <button className="ccfh-pill">{variant === "phone" ? "ES" : "Eric Silver ▾"}</button>
        </div>
      </div>
      <nav className="ccfh-tabs">
        <a href="#" className="is-current">Family Home</a>
        <a href="#">Friends</a>
        <a href="#">Activity</a>
        <a href="#">Media</a>
        {variant === "desktop" && <><a href="#">Blog</a><a href="#">Forum</a><a href="#">Help</a></>}
        <a href="#">Admin ▾</a>
      </nav>

      <main className="ccfh-page">
        {/* Crumbs */}
        <div className="ccfh-crumbs">
          <a href="#">Home</a><span className="sep">/</span><span className="here">Care Circle Family</span>
        </div>

        {/* Masthead */}
        <header className="ccfh-mast">
          <span className="ccfh-mast__corner ccfh-mast__corner--l">Vol. III · No. 142</span>
          <span className="ccfh-mast__corner ccfh-mast__corner--r">Tue · 14 May 2026</span>
          <div className="ccfh-mast__eyebrow">The Family Daily</div>
          <h1 className="ccfh-mast__title">The Silver Family Circle</h1>
          <p className="ccfh-mast__foot">Caring for <strong>Rose Ellis</strong> · Bright with passing clouds, 17° · 5 contributors today</p>
        </header>

        {/* Greeting */}
        <div className="ccfh-greet">
          <p className="ccfh-greet__hi">Welcome back, <em>Eric</em>. Here is the family at a glance.</p>
          <p className="ccfh-greet__meta">Rose's next session in 4 hours · last edition delivered 8:02 am</p>
        </div>

        {/* Today */}
        <section className="ccfh-today">
          <figure className="ccfh-today__photo">
            <span className="ccfh-today__photo-tag"><ProvBadge kind="family">From Lucy · 2 hrs ago</ProvBadge></span>
            <div className="ccfh-today__photo-mark">[ photo · tomato plants in Lucy's allotment ]</div>
            <figcaption className="ccfh-today__photo-cap">"They finally have little green fruits — bringing some Sunday."</figcaption>
          </figure>
          <div className="ccfh-today__copy">
            <p className="ccfh-today__eyebrow">Today in the circle</p>
            <h2 className="ccfh-today__h">Three new contributions, one voice message, and Margaret added to the circle.</h2>
            <p className="ccfh-today__lede">Tomorrow's edition closes at 6:30 pm. Lucy's photo is queued as the lead, James submitted a Sandy update, and Margaret recorded a 48-second message for the great-grandchildren.</p>
            <div className="ccfh-today__metrics">
              <div><div className="ccfh-metric__n">5 <span className="delta">▲ 2</span></div><div className="ccfh-metric__l">Contributors / week</div></div>
              <div><div className="ccfh-metric__n">12</div><div className="ccfh-metric__l">Items queued</div></div>
              <div><div className="ccfh-metric__n">142</div><div className="ccfh-metric__l">Editions sent</div></div>
            </div>
          </div>
        </section>

        {/* Care & Circle */}
        <div className="ccfh-sec">
          <h3 className="ccfh-sec__title">Care &amp; Circle</h3>
          <span className="ccfh-sec__meta">Section A · <a href="#">Manage all →</a></span>
        </div>

        <div className="ccfh-cols">
          <div>
            <div className="ccfh-nav-grid">
              <NavCard accent count="4" suffix="active" title="Friends" sub="Lucy, James, Margaret and Tom — view profiles and contributions." arrow="Open friends →"
                icon={<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"><circle cx="9" cy="9" r="3.5" /><circle cx="17" cy="11" r="3" /><path d="M2 20a7 7 0 0 1 14 0" /><path d="M14 20a6 6 0 0 1 8 0" /></svg>} />
              <NavCard count="6" suffix="seats" title="Members" sub="Manage family circle access and invitations."
                icon={<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"><circle cx="12" cy="8" r="4" /><path d="M4 21a8 8 0 0 1 16 0" /></svg>}
                members={<>
                  <span className="ccfh-avatar">EL</span>
                  <span className="ccfh-avatar ccfh-avatar--stack">JE</span>
                  <span className="ccfh-avatar ccfh-avatar--stack">MA</span>
                  <span className="ccfh-avatar ccfh-avatar--stack">TO</span>
                  <button className="ccfh-invite">+ Invite</button>
                </>} />
              <NavCard count="12" suffix="events" title="Recent Activity" sub="Sessions, comments and engagement events from the last 24 hours." arrow="View ledger →"
                icon={<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"><polyline points="3 17 9 11 13 15 21 7" /><polyline points="14 7 21 7 21 14" /></svg>} />
              <NavCard count="34" suffix="photos" title="Media" sub="Upload family photos for personalised prompts and editions." arrow="Open library →"
                icon={<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"><rect x="3" y="5" width="18" height="14" rx="2" /><circle cx="9" cy="11" r="2" /><path d="M21 17l-5-5-9 7" /></svg>} />
              <NavCard count="9 / 12" suffix="on" title="Providers" sub="Configure auto and curated content sources for daily sessions." arrow="Edit sources →"
                icon={<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"><rect x="3" y="4" width="7" height="16" rx="1.5" /><rect x="14" y="4" width="7" height="16" rx="1.5" /></svg>} />
              <NavCard count="tomorrow" title="Tomorrow's Edition" sub="Preview and reorder sections before the 6:30 pm deadline." arrow="Preview edition →"
                icon={<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"><path d="M4 6h16M4 12h16M4 18h10" /></svg>} />
            </div>
          </div>

          <aside className="ccfh-stack">
            <article className="ccfh-card ccfh-card--ember">
              <button className="ccfh-audio">
                <span className="ccfh-audio__circle"></span>
                <span>
                  <span className="ccfh-audio__meta">Voice · Margaret · 0:48</span>
                  <span className="ccfh-audio__h">"Listen — happy birthday from the great-grandchildren"</span>
                </span>
              </button>
            </article>
            <article className="ccfh-card">
              <ProvBadge kind="curated">On this day · 1953</ProvBadge>
              <div className="ccfh-pull" style={{ marginTop: 10 }}>
                <div className="ccfh-pull__t">"Two men stand on top of the world."</div>
                <div className="ccfh-pull__sub">Hillary and Tenzing summit Everest — three days before Rose's Coronation week as a girl of 13.</div>
              </div>
            </article>
            <article className="ccfh-card">
              <ProvBadge kind="auto">Birthdays this week</ProvBadge>
              <h4 className="ccfh-card__h">Albert &amp; Sandy</h4>
              <p className="ccfh-card__p"><strong>Albert</strong> — would have been 92 today. <strong>Sandy</strong> the spaniel turns 18 next week.</p>
            </article>
            <article className="ccfh-card ccfh-card--garden">
              <ProvBadge kind="auto">Garden almanac</ProvBadge>
              <h4 className="ccfh-card__h">Sweet peas want sowing this week</h4>
              <p className="ccfh-card__p">Soak the seeds overnight. The soil is finally warm enough.</p>
            </article>
          </aside>
        </div>

        {/* Community */}
        <div className="ccfh-sec" style={{ marginTop: 44 }}>
          <h3 className="ccfh-sec__title">Community</h3>
          <span className="ccfh-sec__meta">Section B · <a href="#">All threads →</a></span>
        </div>

        <div className="ccfh-comm">
          <article className="ccfh-card">
            <ProvBadge kind="auto">Recent activity</ProvBadge>
            <ul className="ccfh-ledger" style={{ marginTop: 10 }}>
              <li><span className="ccfh-ledger__t">9:14 am</span><span className="ccfh-ledger__copy"><strong>Lucy</strong> uploaded a photo to Media — "Tomato plants finally fruiting." <small>Queued as tomorrow's lead</small></span><span className="ccfh-ledger__tag">Family</span></li>
              <li><span className="ccfh-ledger__t">8:02 am</span><span className="ccfh-ledger__copy"><strong>Today's edition</strong> delivered to Rose by email. <small>Opened at 8:14 am · read time 6 min</small></span><span className="ccfh-ledger__tag">Auto</span></li>
              <li><span className="ccfh-ledger__t">Yesterday</span><span className="ccfh-ledger__copy"><strong>James</strong> submitted a Sandy update with a photo. <small>Pending review</small></span><span className="ccfh-ledger__tag">Family</span></li>
              <li><span className="ccfh-ledger__t">Yesterday</span><span className="ccfh-ledger__copy"><strong>Margaret</strong> joined the circle and recorded a 48-second voice message. <small>Welcome!</small></span><span className="ccfh-ledger__tag">Family</span></li>
              <li><span className="ccfh-ledger__t">2 days</span><span className="ccfh-ledger__copy"><strong>Hymn of the day</strong> provider switched to weekly rotation. <small>By Eric</small></span><span className="ccfh-ledger__tag">Curated</span></li>
            </ul>
          </article>
          <article className="ccfh-card">
            <ProvBadge kind="curated">Forum · trending</ProvBadge>
            <h4 className="ccfh-card__h">"Best way to read aloud to Mum without tiring her?"</h4>
            <p className="ccfh-card__p">14 replies · 6 family caregivers chiming in this morning.</p>
            <span className="ccfh-nav__arrow" style={{ display: "inline-flex", marginTop: 10 }}>Open thread →</span>
          </article>
          <article className="ccfh-card">
            <ProvBadge kind="auto">Help &amp; tips</ProvBadge>
            <h4 className="ccfh-card__h">Recording good voice messages</h4>
            <p className="ccfh-card__p">A short guide to keeping recordings warm, slow, and easy to follow.</p>
            <span className="ccfh-nav__arrow" style={{ display: "inline-flex", marginTop: 10 }}>Read guide →</span>
          </article>
        </div>

        <p className="ccfh-colophon">— Care Circle Family · Delivered with affection by Ink &amp; Quill —</p>
      </main>
    </div>
  );
}

Object.assign(window, { CareCircleFamilyHome });
