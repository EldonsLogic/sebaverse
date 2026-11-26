import { lesson } from './lesson.js'
import type {
  DemoChoice, DemoChoiceId, DemoFeedback, DemoFraction, GuidedChoiceId, PracticeChoiceId, StartingPoint,
} from './lesson.js'

export type DemoStep = 'intro' | 'explanation' | 'guided' | 'guided-feedback' | 'practice' | 'practice-feedback' | 'summary'

export type DemoState = {
  readonly step: DemoStep
  readonly revision: number
  readonly startingPoint: StartingPoint | null
  readonly hintUsed: boolean
  readonly guidedChoice: GuidedChoiceId | null
  readonly practiceChoice: PracticeChoiceId | null
}

export type DemoAction = Pick<DemoState, 'step' | 'revision'> & (
  | { type: 'start'; startingPoint: StartingPoint }
  | { type: 'choose'; choiceId: DemoChoiceId }
  | { type: 'advance' | 'hint' | 'reset' }
)

type DemoView = {
  title: string
  text: string
  primaryLabel: string
  startingPoints?: readonly { id: StartingPoint; label: string }[]
  equation?: { left: DemoFraction; right: DemoFraction; result?: DemoFraction }
  choices?: readonly DemoChoice[]
  hintLabel?: string
  hint?: string
  feedback?: DemoFeedback
  summary?: { guided: string; practice: string; note: string }
}

export function createDemoState(): DemoState {
  return { step: 'intro', revision: 0, startingPoint: null, hintUsed: false, guidedChoice: null, practiceChoice: null }
}

function allowedChoice<Id extends DemoChoiceId>(choiceId: DemoChoiceId, choices: readonly DemoChoice<Id>[]): choiceId is Id {
  return choices.some((choice) => choice.id === choiceId)
}

const nextStep = {
  explanation: 'guided',
  'guided-feedback': 'practice',
  'practice-feedback': 'summary',
} as const

export function transitionDemo(state: DemoState, action: DemoAction): DemoState {
  if (!action || action.step !== state.step || action.revision !== state.revision) return state

  const revision = state.revision + 1
  switch (action.type) {
    case 'start':
      if (state.step === 'intro' && (action.startingPoint === 'visual' || action.startingPoint === 'notation')) {
        return { ...state, step: 'explanation', revision, startingPoint: action.startingPoint }
      }
      break
    case 'advance':
      if (state.step === 'explanation' || state.step === 'guided-feedback' || state.step === 'practice-feedback') {
        return { ...state, step: nextStep[state.step], revision }
      }
      break
    case 'hint':
      if (state.step === 'guided' && !state.hintUsed) return { ...state, revision, hintUsed: true }
      break
    case 'choose':
      if (state.step === 'guided' && allowedChoice(action.choiceId, lesson.guided.choices)) {
        return { ...state, step: 'guided-feedback', revision, guidedChoice: action.choiceId }
      }
      if (state.step === 'practice' && allowedChoice(action.choiceId, lesson.practice.choices)) {
        return { ...state, step: 'practice-feedback', revision, practiceChoice: action.choiceId }
      }
      break
    case 'reset':
      if (state.step === 'summary') return { ...createDemoState(), revision }
      break
  }
  return state
}

export function getDemoView(state: DemoState): DemoView {
  switch (state.step) {
    case 'intro':
      return lesson.intro
    case 'explanation': {
      const { title, equation, primaryLabel, visual, notation } = lesson.explanation
      return { title, equation, primaryLabel, text: state.startingPoint === 'visual' ? visual : notation }
    }
    case 'guided': {
      const { title, text, equation, choices, hint, hintLabel, primaryLabel } = lesson.guided
      return { title, text, equation, choices, primaryLabel, ...(state.hintUsed ? { hint } : { hintLabel }) }
    }
    case 'guided-feedback': {
      const { title, text, equation, nextLabel } = lesson.guided
      const feedback = state.guidedChoice === null ? undefined : lesson.guided.feedback[state.guidedChoice]
      return { title, text, equation, primaryLabel: nextLabel, feedback }
    }
    case 'practice': {
      const { title, text, equation, choices, primaryLabel } = lesson.practice
      return { title, text, equation, choices, primaryLabel }
    }
    case 'practice-feedback': {
      const { title, text, equation, nextLabel } = lesson.practice
      const feedback = state.practiceChoice === null ? undefined : lesson.practice.feedback[state.practiceChoice]
      return { title, text, equation, primaryLabel: nextLabel, feedback }
    }
    case 'summary': {
      const { title, text, resetLabel, guidedWithHint, guidedWithoutHint, practice, note } = lesson.summary
      return {
        title, text, primaryLabel: resetLabel,
        summary: { guided: state.hintUsed ? guidedWithHint : guidedWithoutHint, practice, note },
      }
    }
  }
}
