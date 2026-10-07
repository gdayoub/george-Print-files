# Validation record

`project_validation.json` is the package-build snapshot and therefore can say `sliced: false`. The later `slicer_estimates.json` and toolpath reports document completed slicing of the delivered project. Physical print/mount/load fields remain untested. Neither a clean mesh nor an empty plate-warning field proves a physical print or safe load.

The source geometry report may predate submicron serialization cleanup. The actual exported STL/embedded-project checks and any serialization/assembly reports describe the final files. Source hashes, exact digital overlap values and method details are retained. See the shared [engineering record](../../../docs/character-homeware/HOMEWARE_ENGINEERING.md).
