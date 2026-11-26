# Local demo lesson content and provenance

25 November 2026 · U27/AUTH-017 · R010/R011/R019/R054/R055/R067/R097. This is one original Egyptian Arabic micro-lesson for the isolated browser demonstration. The goal is to try adding two fractions with the same denominator, using the idea that the size of each piece stays the same. All numerical choices, Arabic explanations, hint and feedback were authored for this demo. The fixture uses no textbook, production curriculum, learner record, external source text or Athar asset. [Founder authorization](../../sources/local-teaching-demo-instruction.md) · [Authored content](../../web/src/demo/lesson.ts)

| Step | Authored example and intention |
| --- | --- |
| Explanation | Choose an equal-piece explanation or fraction notation. Both use 1/5 + 2/5 = 3/5. The denominator names the size of each piece. |
| Guided choice | Work out 2/7 + 3/7. The optional hint asks the learner to count both groups and keep the piece size. It leaves the numerical result to the learner. Feedback follows a submitted choice and addresses adding denominators or counting only one group. |
| Fresh practice | Work out 3/8 + 1/8 before simplification, using different operands, options and denominator. No hint, solution or feedback appears before the choice is submitted. The choices include the sum alongside plausible alternatives with the same presentation. |
| Summary and reset | Report whether the guided hint was used and that the fresh question ran without a hint. The summary makes no attainment or retained-learning judgment. Reset clears both choices, starting preference and hint use. |

The source card labels the explanation as original demo material. The authored answer fixtures are inspectable in the browser and serve only to demonstrate feedback. There is no curriculum alignment claim, educator approval, validated grade or accepted independent evidence. Nobody was recruited, observed or assessed. This document records content design, with arithmetic and state checks specified separately. [Demo state](../../web/src/demo/state.ts) · [Transition tests](../../web/src/demo/state.test.ts) · [Learning quality](../QUALITY-BAR.md#3-learning-quality)

The authored content fingerprint for `web/src/demo/lesson.ts` is SHA-256 `514c744ee6a0902be171ff41bf732862253037c4378547c2f9713919746a9993`. Transition execution is pending the qualified local Node runtime.

26 November recovery annotation: the integrator previously ran all nine transition tests successfully under the independently qualified official Node 24.22.3. The earlier pending statement describes the author's pre-runtime stage. This is not final demo acceptance; use the current commands and remaining verification in [ACTIVE-HANDOFF.md](../ACTIVE-HANDOFF.md).
