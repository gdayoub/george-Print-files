# Agent entry point

Read `Docs/AGENT_HANDOFF.md`, `Docs/HULK_BRIEF.md` and `Docs/PRINTING.md` before making changes.

- `Foundations/Core_Case.3mf` is the dimensional and mechanical master. Preserve its original case body, lid, device cavity, tool slots and mating threads at scale 1. Never substitute the obsolete sleeve-only file.
- Venom V4 Fast is the latest completed printable release. Hulk is planned only; no Hulk model, render, slice or fit check has been completed.
- Build decoration outside the original functional surfaces. Preserve exact source meshes as separately identifiable components in geometry exports. Use rigid transforms only on originals.
- Keep source attribution and license metadata with the foundation model.
- Preserve the current Venom release when creating Hulk. Use a separate design/output directory.
- Check generated mesh integrity, source geometry identity, both opening paths, jar exit and native Bambu slicing when changing geometry.
- Use P1S / 0.4 mm as the current benchmark. Retain 0.20 mm / four-wall thread bands. Generic benchmark filament profiles are not calibrated user profiles.
- Do not claim physical fit, exact tightened face alignment, support removal, durability or odor containment from digital checks alone.
- Do not print/send a printer job or publish/upload the project unless the user requests it.
- `_archive/` is local recovery history, not an active release or a tracked deliverable. Never delete it as part of routine cleanup.
- Keep the Desktop `Prints/Venom` delivery synchronized with completed releases, with a clear status for unfinished work.
