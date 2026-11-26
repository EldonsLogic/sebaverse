import { useEffect, useRef, useState } from 'react';
import type { FormEvent, ReactNode } from 'react';
import { lesson } from './lesson';
import type { DemoFraction } from './lesson';
import { messages } from './messages';
import { createDemoState, getDemoView, transitionDemo } from './state';
import type { DemoAction, DemoState } from './state';

type DemoView = ReturnType<typeof getDemoView>;
type EquationData = NonNullable<DemoView['equation']>;
type Stage = keyof typeof messages.stages;

const stages = ['intro', 'explanation', 'guided', 'practice', 'summary'] as const;
const numbers = new Intl.NumberFormat('ar-EG', { useGrouping: false });

function stageOf(step: DemoState['step']): Stage {
  if (step === 'guided-feedback') return 'guided';
  if (step === 'practice-feedback') return 'practice';
  return step;
}

function fractionText(fraction: DemoFraction) {
  return messages.fraction(numbers.format(fraction.numerator), numbers.format(fraction.denominator));
}

function StackedFraction({ value }: { value: DemoFraction }) {
  return (
    <bdi dir="ltr" className="stacked-fraction" aria-hidden="true">
      <span>{numbers.format(value.numerator)}</span>
      <span>{numbers.format(value.denominator)}</span>
    </bdi>
  );
}

function Equation({ left, right, result }: EquationData) {
  const operation = messages.add(fractionText(left), fractionText(right));
  return (
    <div className="demo-equation">
      <span className="demo-sr-only">
        {result ? messages.equals(operation, fractionText(result)) : messages.unknownResult(operation)}
      </span>
      <bdi dir="ltr" className="demo-equation__parts" aria-hidden="true">
        <StackedFraction value={left} />
        <span>{messages.plusSymbol}</span>
        <StackedFraction value={right} />
        <span>{messages.equalsSymbol}</span>
        {result ? <StackedFraction value={result} /> : <span className="demo-equation__unknown">{messages.questionSymbol}</span>}
      </bdi>
    </div>
  );
}

function FractionBar({ total, blue, orange }: { total: number; blue: number; orange: number }) {
  return (
    <div className="fraction-bar" dir="ltr" aria-hidden="true">
      {Array.from({ length: total }, (_, index) => (
        <span
          key={index}
          className={index < blue ? 'fraction-bar__first' : index < blue + orange ? 'fraction-bar__second' : ''}
        />
      ))}
    </div>
  );
}

function FractionModel({ equation }: { equation?: EquationData }) {
  if (!equation?.result) {
    return (
      <div className="fraction-preview" aria-hidden="true">
        <FractionBar total={5} blue={1} orange={0} />
        <FractionBar total={5} blue={0} orange={2} />
        <FractionBar total={5} blue={1} orange={2} />
      </div>
    );
  }

  return (
    <div className="fraction-model">
      <div className="fraction-model__row">
        <StackedFraction value={equation.left} />
        <span className="demo-sr-only">{fractionText(equation.left)}</span>
        <FractionBar total={equation.left.denominator} blue={equation.left.numerator} orange={0} />
      </div>
      <div className="fraction-model__row">
        <StackedFraction value={equation.right} />
        <span className="demo-sr-only">{fractionText(equation.right)}</span>
        <FractionBar total={equation.right.denominator} blue={0} orange={equation.right.numerator} />
      </div>
      <div className="fraction-model__row fraction-model__row--result">
        <StackedFraction value={equation.result} />
        <span className="demo-sr-only">{fractionText(equation.result)}</span>
        <FractionBar total={equation.result.denominator} blue={equation.left.numerator} orange={equation.right.numerator} />
      </div>
    </div>
  );
}

function StageProgress({ current }: { current: Stage }) {
  const currentIndex = stages.indexOf(current);
  return (
    <ol className="demo-stages" role="list" aria-label={messages.stageLabel}>
      {stages.map((stage, index) => (
        <li key={stage} aria-current={stage === current ? 'step' : undefined} data-current={index <= currentIndex}>
          {messages.stages[stage]}
        </li>
      ))}
    </ol>
  );
}

function PrimaryButton({
  label, type = 'button', disabled = false, onClick,
}: {
  label: string; type?: 'button' | 'submit'; disabled?: boolean; onClick?: () => void;
}) {
  return (
    <button className="demo-primary" type={type} onClick={onClick} disabled={disabled} data-demo-primary>
      <span>{label}</span>
      <span aria-hidden="true" className="demo-next" dir="ltr">{messages.nextSymbol}</span>
    </button>
  );
}

function ChoiceForm<Choice extends string>({
  options, legend, primaryLabel, onSubmit, children, compact = false, selectionHelp = messages.noAnswerSelected,
}: {
  options: readonly { id: Choice; label: ReactNode }[];
  legend: string;
  primaryLabel: string;
  onSubmit: (value: Choice) => void;
  children?: ReactNode;
  compact?: boolean;
  selectionHelp?: string;
}) {
  const [selected, setSelected] = useState<Choice | null>(null);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (selected !== null) onSubmit(selected);
  }

  return (
    <form className="demo-choice-form" onSubmit={submit}>
      <fieldset className="demo-choices" data-compact={compact}>
        <legend>{legend}</legend>
        {options.map(({ id, label }) => (
          <label className="demo-choice" key={id} data-selected={selected === id}>
            <input type="radio" name="demo-choice" value={id} checked={selected === id} onChange={() => setSelected(id)} />
            <span>{label}</span>
          </label>
        ))}
      </fieldset>
      {children}
      <div className="demo-actions">
        <PrimaryButton label={primaryLabel} type="submit" disabled={selected === null} />
        {selected === null && <p className="demo-choice-help">{selectionHelp}</p>}
      </div>
    </form>
  );
}

function SourcePanel({ excerpt }: { excerpt: boolean }) {
  const provenance = <p className="demo-source__label">{lesson.sourceLabel} · {messages.sourceVersion}</p>;
  return (
    <section className="demo-source" aria-label={messages.source}>
      {excerpt ? (
        <details data-demo-source>
          <summary>{messages.sourceOpen}</summary>
          {provenance}
          <p>{messages.sourceExcerpt}</p>
        </details>
      ) : (
        provenance
      )}
    </section>
  );
}

function StudyAside({ stage, equation, feedback }: { stage: Stage; equation?: EquationData; feedback: boolean }) {
  if (stage === 'intro' || stage === 'explanation') {
    const preview = stage === 'intro';
    return (
      <aside className="demo-aside demo-aside--visual" aria-labelledby="demo-aside-heading">
        <h2 id="demo-aside-heading">{preview ? messages.previewTitle : messages.diagramTitle}</h2>
        <FractionModel equation={preview ? undefined : equation} />
        <p>{preview ? messages.previewText : messages.diagramText}</p>
      </aside>
    );
  }
  const copy = feedback ? [messages.feedbackAsideTitle, messages.feedbackAsideText] : {
    guided: [messages.guidedAsideTitle, messages.guidedAsideText],
    practice: [messages.practiceAsideTitle, messages.practiceAsideText],
    summary: [messages.summaryAsideTitle, messages.summaryAsideText],
  }[stage];
  return (
    <aside className="demo-aside demo-aside--quiet" aria-labelledby="demo-aside-heading">
      <h2 id="demo-aside-heading">{copy[0]}</h2>
      <p>{copy[1]}</p>
    </aside>
  );
}

export function Demo() {
  const [state, setState] = useState(createDemoState);
  const view = getDemoView(state);
  const stage = stageOf(state.step);
  const heading = useRef<HTMLHeadingElement>(null);
  const previousStep = useRef(state.step);
  const snapshot = { step: state.step, revision: state.revision };
  const explainVisually = state.step === 'explanation' && state.startingPoint === 'visual';
  const aside = <StudyAside stage={stage} equation={view.equation} feedback={Boolean(view.feedback)} />;
  const title = state.step === 'intro' ? lesson.title : view.feedback?.title ?? view.title;

  useEffect(() => {
    if (previousStep.current !== state.step) {
      heading.current?.focus();
      previousStep.current = state.step;
    }
  }, [state.step]);

  function send(action: DemoAction) {
    setState((current) => transitionDemo(current, action));
  }

  return (
    <>
      <a className="demo-skip" href="#demo-main">{messages.skip}</a>
      <header className="demo-header">
        <div className="demo-container demo-header__inner">
          <img className="demo-logo" src="/brand/sebaverse-primary-color.svg" alt={messages.brand} width="610" height="95" />
          <p className="demo-mode"><span aria-hidden="true" />{lesson.label}</p>
        </div>
      </header>
      <main className="demo-container demo-main" id="demo-main" tabIndex={-1} data-demo-stage={state.step}>
        <StageProgress current={stage} />
        <div className="demo-workspace" data-visual-first={explainVisually}>
          {explainVisually && aside}
          <article className="demo-panel" aria-labelledby="demo-heading">
            <header>
              {stage !== 'intro' && <p className="demo-topic">{lesson.title}</p>}
              <h1 id="demo-heading" ref={heading} tabIndex={-1}>{title}</h1>
              {!view.feedback && <p className="demo-lede">{view.text}</p>}
            </header>

            {view.equation && <Equation {...view.equation} />}

            {state.step === 'intro' && view.startingPoints && view.primaryLabel && (
              <ChoiceForm
                key={state.step}
                options={view.startingPoints.map(({ id, label }) => ({ id, label }))}
                legend={view.title}
                primaryLabel={view.primaryLabel}
                onSubmit={(startingPoint) => send({ ...snapshot, type: 'start', startingPoint })}
                selectionHelp={messages.noStartingPointSelected}
              />
            )}

            {(state.step === 'guided' || state.step === 'practice') && view.choices && view.primaryLabel && (
              <ChoiceForm
                key={state.step}
                options={view.choices.map(({ id, fraction }) => ({
                  id, label: <><StackedFraction value={fraction} /><span className="demo-sr-only">{fractionText(fraction)}</span></>,
                }))}
                legend={state.step === 'guided' ? messages.guidedChoice : messages.practiceChoice}
                primaryLabel={view.primaryLabel}
                onSubmit={(choiceId) => send({ ...snapshot, type: 'choose', choiceId })}
                compact
              >
                {state.step === 'guided' && (
                  <div className="demo-hint">
                    <button
                      className="demo-quiet"
                      type="button"
                      aria-disabled={state.hintUsed}
                      aria-expanded={state.hintUsed}
                      aria-controls="demo-hint-text"
                      data-demo-hint
                      onClick={() => {
                        if (!state.hintUsed) send({ ...snapshot, type: 'hint' });
                      }}
                    >
                      {state.hintUsed ? messages.hintShown : view.hintLabel}
                    </button>
                    <div id="demo-hint-text" role="status">
                      {view.hint && <p>{view.hint}</p>}
                    </div>
                  </div>
                )}
              </ChoiceForm>
            )}

            {view.feedback && (
              <p className="demo-feedback" data-tone={view.feedback.tone} data-demo-feedback>{view.feedback.text}</p>
            )}

            {view.summary && (
              <div className="demo-recap">
                <dl>
                  <div><dt>{messages.guidedSummary}</dt><dd>{view.summary.guided}</dd></div>
                  <div><dt>{messages.practiceSummary}</dt><dd>{view.summary.practice}</dd></div>
                </dl>
                <p>{view.summary.note}</p>
              </div>
            )}

            {view.primaryLabel && state.step !== 'intro' && state.step !== 'guided' && state.step !== 'practice' && (
              <div className="demo-actions">
                <PrimaryButton
                  label={view.primaryLabel}
                  onClick={() => send({ ...snapshot, type: state.step === 'summary' ? 'reset' : 'advance' })}
                />
              </div>
            )}
          </article>
          {!explainVisually && aside}
        </div>
        <footer className="demo-footer">
          <SourcePanel key={stage} excerpt={stage === 'explanation' || stage === 'guided'} />
          <p>{messages.localFixture}</p>
        </footer>
      </main>
    </>
  );
}
