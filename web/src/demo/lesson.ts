export type StartingPoint = 'visual' | 'notation'
export type GuidedChoiceId = 'guided-size' | 'guided-total' | 'guided-second'
export type PracticeChoiceId = 'practice-first' | 'practice-size' | 'practice-total'
export type DemoChoiceId = GuidedChoiceId | PracticeChoiceId

export type DemoFraction = { readonly numerator: number; readonly denominator: number }
export type DemoChoice<Id extends DemoChoiceId = DemoChoiceId> = {
  readonly id: Id
  readonly fraction: DemoFraction
}
export type DemoFeedback = {
  readonly title: string
  readonly text: string
  readonly tone: 'positive' | 'next-step'
}

function freezeContent<T extends object>(value: T): Readonly<T> {
  for (const child of Object.values(value)) {
    if (child !== null && typeof child === 'object') freezeContent(child)
  }
  return Object.freeze(value)
}

export const lesson = freezeContent({
  title: 'نجمع كسور ليها نفس المقام',
  label: 'عرض تعليمي محلي',
  sourceLabel: 'بطاقة القاعدة · محتوى أصلي للتجربة',
  intro: {
    title: 'تحب تبدأ بإيه؟',
    text: 'لما الأجزاء تكون قدّ بعض، إزاي نجمعها؟ اختار الطريقة اللي تحب تشوف بيها المثال.',
    startingPoints: [
      { id: 'visual', label: 'أشوفها كقطع متساوية' },
      { id: 'notation', label: 'أشوفها ككسور مكتوبة' },
    ],
    primaryLabel: 'شوف المثال',
  },
  explanation: {
    title: 'نعدّ القطع ونخلّي حجمها زي ما هو',
    visual: 'تخيّل شريطين متقسّمين لخمس قطع متساوية. ناخد خُمس من الأول وخُمسين من التاني. المجموع تلات قطع، وكل قطعة لسه خُمس.',
    notation: 'لما المقام يكون واحد، بنجمع البسطين ونكتب نفس المقام. هنا ١ زائد ٢ يساوي ٣، والمقام يفضل ٥.',
    equation: {
      left: { numerator: 1, denominator: 5 },
      right: { numerator: 2, denominator: 5 },
      result: { numerator: 3, denominator: 5 },
    },
    primaryLabel: 'جرّب معايا',
  },
  guided: {
    title: 'نجمع خطوة خطوة',
    text: 'معاك سُبعين، وزوّدت عليهم تلات أسباع. اختار المجموع.',
    equation: { left: { numerator: 2, denominator: 7 }, right: { numerator: 3, denominator: 7 } },
    choices: [
      { id: 'guided-size', fraction: { numerator: 5, denominator: 14 } },
      { id: 'guided-total', fraction: { numerator: 5, denominator: 7 } },
      { id: 'guided-second', fraction: { numerator: 3, denominator: 7 } },
    ] satisfies readonly DemoChoice<GuidedChoiceId>[],
    hintLabel: 'عايز تلميح؟',
    hint: 'عدّ القطع في المجموعتين. المقام بيقول حجم القطعة، والحجم ما اتغيّرش.',
    primaryLabel: 'ثبّت اختيارك',
    nextLabel: 'جرّب سؤال جديد',
    feedback: {
      'guided-size': {
        title: 'المقام اتغيّر',
        text: 'البسط ٥ مظبوط. المقام ١٤ هيغيّر حجم القطعة. القطع كلها أسباع، فخلّي المقام ٧.',
        tone: 'next-step',
      },
      'guided-total': {
        title: 'جمعت البسطين وثبّتّ المقام',
        text: 'حسبت القطع من المجموعتين: ٢ زائد ٣. كل قطعة لسه سُبع، فالمجموع خمسة أسباع.',
        tone: 'positive',
      },
      'guided-second': {
        title: 'ناقص قطع من المجموعة الأولى',
        text: 'المقام ٧ صح. البسط ٣ بيعدّ المجموعة التانية بس. ضيف السُبعين اللي بدأت بيهم.',
        tone: 'next-step',
      },
    } satisfies Record<GuidedChoiceId, DemoFeedback>,
  },
  practice: {
    title: 'سؤال جديد من غير تلميح',
    text: 'اختار مجموع الكسرين قبل التبسيط. خُد وقتك.',
    equation: { left: { numerator: 3, denominator: 8 }, right: { numerator: 1, denominator: 8 } },
    choices: [
      { id: 'practice-first', fraction: { numerator: 3, denominator: 8 } },
      { id: 'practice-size', fraction: { numerator: 4, denominator: 16 } },
      { id: 'practice-total', fraction: { numerator: 4, denominator: 8 } },
    ] satisfies readonly DemoChoice<PracticeChoiceId>[],
    primaryLabel: 'ثبّت اختيارك',
    nextLabel: 'شوف الملخّص',
    feedback: {
      'practice-first': {
        title: 'ناقص التُمن اللي اتضاف',
        text: 'التلات أثمان موجودين في البداية. عدّ معاهم التُمن اللي اتضاف، وسيب المقام ٨.',
        tone: 'next-step',
      },
      'practice-size': {
        title: 'المقام اتغيّر',
        text: '٣ زائد ١ يساوي ٤. لو كتبت ١٦ هيتغيّر حجم القطعة. خليك على ٨ لأن القطع كلها أثمان.',
        tone: 'next-step',
      },
      'practice-total': {
        title: 'جمعت أربع قطع بنفس الحجم',
        text: '٣ زائد ١ يساوي ٤. كل قطعة لسه تُمن، فالمجموع أربعة أثمان.',
        tone: 'positive',
      },
    } satisfies Record<PracticeChoiceId, DemoFeedback>,
  },
  summary: {
    title: 'خلصت التجربة',
    text: 'لما المقام يكون واحد، بنجمع البسطين ونخلّي المقام زي ما هو.',
    guidedWithHint: 'استخدمت تلميح في السؤال الموجّه.',
    guidedWithoutHint: 'جرّبت السؤال الموجّه من غير تلميح.',
    practice: 'جاوبت على سؤال جديد من غير تلميح.',
    note: 'ده ملخّص للتجربة المحلية. مفيش درجة أو نتيجة محفوظة.',
    resetLabel: 'ابدأ من جديد',
  },
} as const)
