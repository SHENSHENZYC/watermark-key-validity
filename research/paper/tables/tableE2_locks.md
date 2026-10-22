Table — The four pre-run locks and their records: the protocol, the lock date, the checkpoint whose agreement preceded it, the number of pinned files (the protocol, grid, code, validation record, manifests and, from Study 2 on, the earlier studies' pinned files), the lock's digest, the commit at launch, the run's start and duration, the record's file count and inventory digest, the locked analyser's results digest, and whether the lock opened the holdout (`final`). Every lock carries `before_outcomes: true` and `approved_by: Yichen`; the runners refuse to start without the verified lock and the analysers recompute under it.

| Study | Protocol | Locked | After | Pinned files | Lock digest | Launch commit | Run start (UTC) | Hours | Record files | Inventory digest | Results digest | Holdout opened |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `STUDY1_PROTOCOL_v0.3.md` | 2026-10-10 | R03 | 8 | `ff265b500f0d` | `efa548c` | 2026-10-10 03:26 | 1.49 | 1,248 | `a9fd2cf88b76` | `d9427321d27e` | no |
| 2 | `STUDY2_PROTOCOL_v0.1.md` | 2026-10-12 | R05 | 15 | `434d8f3d8210` | `74a52e0` | 2026-10-13 13:45 | 4.85 | 3,468 | `f3b4a0ceb246` | `069ee14def85` | no |
| 3 | `STUDY3_PROTOCOL_v0.1.md` | 2026-10-15 | R07 | 20 | `0e2889287d9d` | `5e44a2e` | 2026-10-15 19:47 | 0.97 | 240 | `c270ab818620` | `42bb915363fd` | no |
| 4 | `STUDY4_PROTOCOL_v0.1.md` | 2026-10-16 | R09 | 32 | `7067b4e1457c` | `f5dcd60` | 2026-10-17 02:13 | 11.86 | 1,860 | `2c6863586e8f` | `5ee9842146d8` | no |
