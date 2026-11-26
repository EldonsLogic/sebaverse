import assert from 'node:assert/strict'
import { test } from 'node:test'

import { lesson } from './lesson.js'
import type { DemoChoiceId, StartingPoint } from './lesson.js'
import { createDemoState, getDemoView, transitionDemo } from './state.js'
import type { DemoAction, DemoState } from './state.js'

function snapshot(state: DemoState) {
  return { step: state.step, revision: state.revision }
}

function start(state: DemoState, startingPoint: StartingPoint) {
  return transitionDemo(state, { ...snapshot(state), type: 'start', startingPoint })
}

function advance(state: DemoState) {
  return transitionDemo(state, { ...snapshot(state), type: 'advance' })
}

function choose(state: DemoState, choiceId: DemoChoiceId) {
  return transitionDemo(state, { ...snapshot(state), type: 'choose', choiceId })
}

function atGuided() {
  return advance(start(createDemoState(), 'visual'))
}

test('a learner selects the explanation before seeing the guided question', () => {
  const intro = Object.freeze(createDemoState())
  assert.deepEqual(getDemoView(intro).startingPoints?.map(({ id }) => id), ['visual', 'notation'])
  assert.strictEqual(advance(intro), intro)
  assert.equal(getDemoView(intro).equation, undefined)

  const visual = start(intro, 'visual')
  const notation = start(intro, 'notation')
  assert.equal(visual.step, 'explanation')
  assert.equal(notation.step, 'explanation')
  assert.equal(visual.startingPoint, 'visual')
  assert.equal(notation.startingPoint, 'notation')
  assert.notEqual(getDemoView(visual).text, getDemoView(notation).text)
  assert.deepEqual(getDemoView(visual).equation, getDemoView(notation).equation)
  assert.deepEqual(getDemoView(visual).equation?.result, { numerator: 3, denominator: 5 })
  assert.equal(getDemoView(visual).choices, undefined)
  assert.equal(advance(visual).step, 'guided')
  assert.deepEqual(intro, createDemoState())
})

test('the guided choice must be submitted before the view shows targeted feedback', () => {
  const guided = Object.freeze(atGuided())
  const active = getDemoView(guided)
  assert.equal(active.feedback, undefined)
  assert.equal(active.equation?.result, undefined)
  assert.equal(active.hint, undefined)
  assert.equal(active.choices?.length, 3)
  assert.ok(active.choices?.every((choice) => !('feedback' in choice) && !('correct' in choice)))
  assert.strictEqual(advance(guided), guided)

  const submitted = choose(guided, 'guided-size')
  assert.equal(submitted.step, 'guided-feedback')
  assert.equal(submitted.guidedChoice, 'guided-size')
  assert.equal(guided.guidedChoice, null)
  const feedback = getDemoView(submitted)
  assert.equal(feedback.choices, undefined)
  assert.equal(feedback.feedback?.tone, 'next-step')
  assert.match(feedback.feedback?.text ?? '', /٥.*١٤.*٧/)
})

test('the optional hint is recorded once and a stale pre-hint choice stays rejected', () => {
  const guided = atGuided()
  const delayedChoice = { ...snapshot(guided), type: 'choose', choiceId: 'guided-total' } as const
  const hintRequest = { ...snapshot(guided), type: 'hint' } as const
  const hinted = transitionDemo(guided, hintRequest)
  assert.equal(hinted.step, 'guided')
  assert.equal(hinted.hintUsed, true)
  assert.equal(guided.hintUsed, false)
  assert.match(getDemoView(hinted).hint ?? '', /الحجم ما اتغيّرش/)
  assert.equal(getDemoView(hinted).equation?.result, undefined)
  assert.equal(getDemoView(hinted).feedback, undefined)
  assert.strictEqual(transitionDemo(hinted, hintRequest), hinted)
  assert.strictEqual(transitionDemo(hinted, { ...snapshot(hinted), type: 'hint' }), hinted)
  assert.strictEqual(transitionDemo(hinted, delayedChoice), hinted)

  const submitted = choose(hinted, 'guided-total')
  assert.equal(submitted.step, 'guided-feedback')
  assert.equal(submitted.hintUsed, true)
  assert.equal(getDemoView(submitted).feedback?.tone, 'positive')
  assert.strictEqual(transitionDemo(submitted, { ...snapshot(submitted), type: 'hint' }), submitted)
})

test('fresh practice has different operands and accepts only its own choices without hints', () => {
  const guided = atGuided()
  const practice = advance(choose(guided, 'guided-total'))
  const guidedView = getDemoView(guided)
  const active = getDemoView(practice)
  assert.equal(practice.step, 'practice')
  assert.deepEqual(active.equation, {
    left: { numerator: 3, denominator: 8 }, right: { numerator: 1, denominator: 8 },
  })
  assert.notDeepEqual(active.equation, guidedView.equation)
  assert.ok(active.choices?.every(({ id }) => !guidedView.choices?.some((choice) => choice.id === id)))
  assert.equal(active.hint, undefined)
  assert.equal(active.hintLabel, undefined)
  assert.equal(active.feedback, undefined)
  assert.strictEqual(transitionDemo(practice, { ...snapshot(practice), type: 'hint' }), practice)
  assert.strictEqual(choose(practice, 'guided-total'), practice)
  assert.strictEqual(advance(practice), practice)

  const answered = choose(practice, 'practice-total')
  assert.equal(answered.step, 'practice-feedback')
  assert.equal(getDemoView(answered).choices, undefined)
  assert.equal(getDemoView(answered).feedback?.tone, 'positive')
  assert.strictEqual(choose(answered, 'practice-size'), answered)
})

test('invalid actions and earlier submissions do not mutate the current step', () => {
  const guided = Object.freeze(atGuided())
  assert.strictEqual(choose(guided, 'practice-total'), guided)
  const unknownChoice = { ...snapshot(guided), type: 'choose', choiceId: 'unlisted' } as unknown as DemoAction
  assert.strictEqual(transitionDemo(guided, unknownChoice), guided)
  const unknownType = { ...snapshot(guided), type: 'finish' } as unknown as DemoAction
  assert.strictEqual(transitionDemo(guided, unknownType), guided)
  assert.strictEqual(transitionDemo(guided, { ...snapshot(guided), type: 'reset' }), guided)
  assert.strictEqual(start(guided, 'notation'), guided)
  const submitted = { ...snapshot(guided), type: 'choose', choiceId: 'guided-second' } as const
  const feedback = transitionDemo(guided, submitted)
  assert.strictEqual(transitionDemo(feedback, submitted), feedback)
  const practice = advance(feedback)
  assert.strictEqual(transitionDemo(practice, submitted), practice)
  assert.equal(practice.guidedChoice, 'guided-second')
  assert.equal(practice.practiceChoice, null)
})

for (const usedHint of [false, true]) {
  test(`the finished summary reports hint use accurately when usedHint=${usedHint}`, () => {
    let guided = atGuided()
    if (usedHint) guided = transitionDemo(guided, { ...snapshot(guided), type: 'hint' })
    const practice = advance(choose(guided, 'guided-total'))
    const answered = choose(practice, 'practice-first')
    assert.equal(getDemoView(answered).feedback?.tone, 'next-step')
    const summary = advance(answered)
    assert.equal(summary.step, 'summary')
    assert.equal(summary.hintUsed, usedHint)
    assert.deepEqual(getDemoView(summary).summary, {
      guided: usedHint ? 'استخدمت تلميح في السؤال الموجّه.' : 'جرّبت السؤال الموجّه من غير تلميح.',
      practice: 'جاوبت على سؤال جديد من غير تلميح.',
      note: 'ده ملخّص للتجربة المحلية. مفيش درجة أو نتيجة محفوظة.',
    })
    assert.deepEqual(Object.keys(summary).sort(), [
      'guidedChoice', 'hintUsed', 'practiceChoice', 'revision', 'startingPoint', 'step',
    ])
    assert.strictEqual(advance(summary), summary)
  })
}

test('reset clears every answer and hint and rejects actions from the previous intro', () => {
  const initial = createDemoState()
  const oldStart = { ...snapshot(initial), type: 'start', startingPoint: 'visual' } as const
  const guided = advance(transitionDemo(initial, oldStart))
  const hinted = transitionDemo(guided, { ...snapshot(guided), type: 'hint' })
  const summary = advance(choose(advance(choose(hinted, 'guided-total')), 'practice-size'))
  assert.equal(summary.step, 'summary')

  const reset = transitionDemo(summary, { ...snapshot(summary), type: 'reset' })
  assert.deepEqual(reset, { ...createDemoState(), revision: summary.revision + 1 })
  assert.deepEqual(getDemoView(reset), getDemoView(initial))
  assert.strictEqual(transitionDemo(reset, oldStart), reset)
  assert.equal(start(reset, 'notation').startingPoint, 'notation')
})

test('authored content stays frozen and each question has a unique equal-denominator sum', () => {
  assert.ok(Object.isFrozen(lesson))
  assert.ok(Object.isFrozen(lesson.explanation.equation.result))
  const example = lesson.explanation.equation
  assert.equal(example.left.denominator, example.right.denominator)
  assert.equal(example.left.denominator, example.result.denominator)
  assert.equal(example.left.numerator + example.right.numerator, example.result.numerator)

  for (const question of [lesson.guided, lesson.practice]) {
    assert.ok(Object.isFrozen(question.choices))
    assert.ok(question.choices.every(({ fraction }) => Object.isFrozen(fraction)))
    const { left, right } = question.equation
    assert.equal(left.denominator, right.denominator)
    const sums = question.choices.filter(({ fraction }) => (
      fraction.denominator === left.denominator && fraction.numerator === left.numerator + right.numerator
    ))
    assert.equal(sums.length, 1)
  }
})

test('feedback shows the submitted answer and only the true sum is marked positive', () => {
  const guided = atGuided()
  assert.equal(getDemoView(guided).chosen, undefined)
  for (const question of [lesson.guided, lesson.practice]) {
    const { left, right } = question.equation
    for (const choice of question.choices) {
      const atQuestion = question === lesson.guided ? guided : advance(choose(guided, 'guided-total'))
      assert.equal(getDemoView(atQuestion).chosen, undefined)
      const view = getDemoView(choose(atQuestion, choice.id))
      assert.deepEqual(view.chosen, choice.fraction)
      const isSum = choice.fraction.denominator === left.denominator
        && choice.fraction.numerator === left.numerator + right.numerator
      assert.equal(view.feedback?.tone, isSum ? 'positive' : 'next-step')
      if (!isSum) assert.doesNotMatch(view.feedback?.title ?? '', /صح|مظبوط/)
    }
  }
})
