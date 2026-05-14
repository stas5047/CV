## Phase 29 - Frontend experiments and metrics page

**Direction:** Frontend  
**Goal:** Implement experiment visualization with robust empty states.

### Scope

- Implement `/experiments` page.
- Display:
  - model comparison table;
  - confidence threshold analysis chart;
  - tracker behavior comparison table;
  - false-positive analysis summary;
  - precision/recall/mAP cards;
  - FPS/latency chart;
  - confusion matrix image if available.
- Use Recharts for frontend charts.
- Do not use Matplotlib in frontend UI.
- Use the exact Ukrainian empty-state text for missing experiment sections:

```text
Дані експерименту ще не завантажено
```

- Do not render blank chart canvases without explanation.
- Do not show raw `null` values.
- Regular users see published experiments only.
- Admins can see all experiments where backend allows it.
- Use wording `tracker behavior comparison`, not absolute tracking accuracy.

### Relevant docs

- `docs/FRONTEND_UX.md`
- `docs/API.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/TESTING_QA.md`

### Validation

- Experiments route is protected.
- Missing data shows required Ukrainian text.
- Null metric values do not crash the UI.
- Recharts render when data exists.
- Regular user/admin visibility matches backend.
- Frontend build passes.

### Commit

`feat(frontend-experiments): add experiment metrics and empty states`