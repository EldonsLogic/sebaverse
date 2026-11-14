import { useEffect, useRef } from 'react';
import { Link, NavLink, Route, Routes, useLocation } from 'react-router';
import { EmptyState } from '../ui/EmptyState';
import { Icon } from '../ui/Icon';
import type { IconName } from '../ui/Icon';

const navigation: { to: string; label: string; icon: IconName }[] = [
  { to: '/', label: 'الرئيسية', icon: 'home' },
  { to: '/materials', label: 'موادي', icon: 'book' },
  { to: '/practice', label: 'التدريب', icon: 'practice' },
  { to: '/progress', label: 'تقدّمي', icon: 'progress' },
];
const titles: Record<string, string> = { '/': 'الرئيسية', '/materials': 'موادي', '/practice': 'التدريب', '/progress': 'تقدّمي' };

export function App() {
  const location = useLocation();
  const main = useRef<HTMLElement>(null);
  const previousPath = useRef(location.pathname);
  useEffect(() => {
    document.title = `Sebaverse | ${titles[location.pathname] ?? 'الصفحة غير موجودة'}`;
    if (previousPath.current !== location.pathname) main.current?.focus({ preventScroll: true });
    previousPath.current = location.pathname;
    window.scrollTo(0, 0);
  }, [location.pathname]);

  return (
    <>
      <a className="skip-link" href="#main-content">انتقل للمحتوى</a>
      <header className="site-header">
        <div className="header-inner">
          <Link to="/" aria-label="Sebaverse — الرئيسية" className="brand-link"><img className="brand-logo" src="/brand/sebaverse-primary-color.svg" alt="Sebaverse" width="610" height="95" /></Link>
          <div className="header-note"><span className="status-dot" aria-hidden="true" /><span>نسخة أولية</span></div>
        </div>
      </header>
      <div className="app-layout">
        <aside className="sidebar">
          <p className="nav-heading">مساحة التعلّم</p>
          <nav aria-label="التنقّل الرئيسي" className="primary-nav">
            {navigation.map(({ to, label, icon }) => <NavLink key={to} to={to} end={to === '/'} className={({ isActive }) => `nav-link${isActive ? ' is-active' : ''}`}><Icon name={icon} /><span>{label}</span></NavLink>)}
          </nav>
          <div className="sidebar-note"><span className="mini-mark" aria-hidden="true">+</span><p>خُد وقتك.<br />خطوة واضحة أحسن من خطوة مستعجلة.</p></div>
        </aside>
        <main id="main-content" ref={main} tabIndex={-1} className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/materials" element={<Materials />} />
            <Route path="/practice" element={<Practice />} />
            <Route path="/progress" element={<Progress />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
          <footer className="page-footer"><bdi>Sebaverse</bdi><span>مساحة للشرح والتدريب، خطوة بخطوة.</span></footer>
        </main>
      </div>
    </>
  );
}

function PageHeader({ eyebrow, title, description }: { eyebrow: string; title: string; description: string }) {
  return <div className="page-heading"><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p className="lead">{description}</p></div>;
}

function Home() {
  return (
    <>
      <div className="welcome-line"><span>أهلًا بيك في <bdi>Sebaverse</bdi></span><span className="small-note">بداية بسيطة، على مهلك</span></div>
      <section className="hero" aria-labelledby="home-title">
        <div className="hero-copy"><p className="eyebrow">مساحتك للتعلّم</p><h1 id="home-title">نبدأ من اللي<br /><span>بتذاكره.</span></h1><p>رتّب محتواك الدراسي، وارجع للشرح والتدريب في مكان واحد.</p><div className="hero-actions"><Link className="button primary" to="/materials">شوف موادك<Icon name="arrow" /></Link><a className="text-link" href="#getting-started">خطوات البداية</a></div></div>
        <div className="hero-visual" aria-hidden="true"><div className="visual-circle" /><div className="paper paper-back" /><div className="paper paper-front"><div className="paper-top"><span /><span /><span /></div><div className="paper-line wide" /><div className="paper-line" /><div className="paper-highlight"><Icon name="check" /><span /></div><div className="paper-line short" /><div className="paper-line" /></div><div className="floating-symbol"><Icon name="book" /></div><div className="orange-spark">✦</div></div>
      </section>
      <div className="initial-notice"><span className="notice-marker" aria-hidden="true" /><p>دي نسخة أولية. لسه مفيش مواد أو حسابات مضافة، والرفع والشرح مش متاحين دلوقتي.</p></div>
      <section className="overview" aria-labelledby="overview-title"><div className="section-heading"><h2 id="overview-title">كل خطوة ليها مكان</h2><p>اختار المساحة اللي عايز تشوفها.</p></div><div className="feature-grid">{navigation.slice(1).map(({ to, label, icon }, i) => <Link to={to} className="feature-card" key={to}><span className={`feature-icon tone-${i}`}><Icon name={icon} /></span><h3>{label}</h3><p>{['المحتوى اللي هتضيفه هيتجمع هنا، مع معلومات مصدره وإصداره.', 'مساحة للأسئلة والمراجعة، بعد إضافة المحتوى المناسب.', 'تابع ما اتدرّبت عليه وما لسه محتاج مراجعة، لما تبدأ.'][i]}</p><span className="feature-link">افتح المساحة<Icon name="arrow" /></span></Link>)}</div></section>
      <section className="getting-started" id="getting-started" aria-labelledby="steps-title"><div><p className="eyebrow">لما إضافة المحتوى تبقى متاحة</p><h2 id="steps-title">بداية واضحة، من غير استعجال.</h2></div><ol className="steps"><li><span>١</span><div><h3>أضف محتواك الدراسي</h3><p>منهج أو ملاحظات عندك الحق في استخدامها.</p></div></li><li><span>٢</span><div><h3>راجع المادة والمصدر</h3><p>اتأكد من الصفحات والإصدار قبل ما تبدأ.</p></div></li><li><span>٣</span><div><h3>ابدأ الشرح والتدريب</h3><p>خد تلميح لما تحتاج، وبعدها جرّب بنفسك.</p></div></li></ol></section>
    </>
  );
}

function Materials() {
  return <><PageHeader eyebrow="المحتوى الدراسي" title="موادي" description="هنا هتلاقي المواد والملفات اللي بتذاكر منها، مع مصدر كل ملف وإصداره." /><EmptyState icon="book" title="لسه مفيش مواد مضافة"><p>لما إضافة المحتوى تبقى متاحة، هتقدر تبدأ بالمادة اللي بتذاكرها. مفيش مادة أو مستوى دراسي مختار عنك.</p><p className="availability-note">رفع الملفات مش متاح في النسخة الأولية دي.</p></EmptyState><details className="info-details"><summary>إيه اللي مهم قبل إضافة أي ملف؟</summary><div><ul><li>يكون عندك الحق في استخدام الملف للتعلّم.</li><li>تراجع اسم المادة وإصدار المنهج والصفحات.</li><li>ملفاتك الخاصة ما تتحوّلش لمحتوى عام تلقائيًا.</li></ul><p>تفاصيل الرفع والخصوصية هتظهر قبل ما ترفع أي محتوى.</p></div></details></>;
}

function Practice() {
  return <><PageHeader eyebrow="أسئلة ومراجعة" title="التدريب" description="مساحة للتدرّب على محتواك الدراسي، مع تمييز التدريب بمساعدة عن المحاولة المستقلة." /><EmptyState icon="practice" title="التدريب لسه ما بدأش" action={<Link className="button primary" to="/materials">شوف مساحة المواد<Icon name="arrow" /></Link>}><p>مفيش محتوى أو أسئلة مضافة حاليًا. لما يكون فيه محتوى جاهز للتدريب، هتلاقيه هنا.</p></EmptyState><div className="explanation-card"><span className="feature-icon tone-1"><Icon name="check" /></span><div><h2>التلميح مساعدة، مش امتحان.</h2><p>لما تبدأ التدريب، المحاولة بعد تلميح هتفضل مختلفة عن الإجابة المستقلة. مفيش نتائج أو درجات محسوبة في النسخة دي.</p></div></div></>;
}

function Progress() {
  return <><PageHeader eyebrow="فهم أوضح لتعلّمك" title="تقدّمي" description="اعرف ما اتدرّبت عليه، وإيه اللي لسه محتاج مراجعة، من غير أحكام أو نسب مش مبنية على تدريب فعلي." /><EmptyState icon="progress" title="لسه مفيش تقدّم مسجّل" action={<Link className="button secondary" to="/practice">شوف مساحة التدريب<Icon name="arrow" /></Link>}><p>التقدّم هيظهر بعد وجود تدريبات ومحاولات فعلية. عدم وجود بيانات ما يعنيش إن مستواك ضعيف.</p></EmptyState><section className="progress-principles" aria-labelledby="progress-principles-title"><h2 id="progress-principles-title">إيه اللي هيوضّحه تقدّمك؟</h2><ul><li><Icon name="check" />اللي جاوبته بشكل مستقل.</li><li><Icon name="check" />اللي اتدرّبت عليه بمساعدة.</li><li><Icon name="check" />اللي لسه محتاج تجربة أو مراجعة.</li></ul></section></>;
}

function NotFound() {
  return <><PageHeader eyebrow="مش لاقيين الصفحة دي" title="نرجع لمساحة التعلّم؟" description="ممكن يكون رابط الصفحة اتغيّر. تقدر تبدأ من الرئيسية." /><Link to="/" className="button primary">ارجع للرئيسية<Icon name="arrow" /></Link></>;
}
