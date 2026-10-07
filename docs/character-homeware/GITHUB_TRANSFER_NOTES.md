# GitHub publication handoff

## Authorization and destination

The user explicitly authorized publishing the print files and research Markdown to their existing prints repository. The destination is `gdayoub/george-Print-files`, preserving its existing visibility and unrelated content. The root agent coordinates the final commit and branch update. This helper uploads only immutable Git blobs; an uploaded blob alone does not change a branch or publish a release.

## Confirmed transport behavior

Local Git credential discovery was unavailable in this session, while the connected GitHub tools worked. No browser session or credential extraction was used.

The shell tool's output is capped near 1 MiB even if `max_output_tokens` requests more. Reading an entire 3 MB 3MF as base64 therefore truncated the result. The verified workaround uses 600,000-byte local chunks, assembled privately in `functions.exec`, with one `github_create_blob` call per file. Chunk size is divisible by three, so concatenating the base64 chunks is valid. Tool outputs containing base64 are never printed with `text()` or `notify()`.

Each upload checks expected base64 length and compares the returned SHA against a local Git blob hash: SHA-1 of `blob <byte-count>\\0` followed by the exact file bytes. SHA-256 is also recorded for delivery comparisons. A mismatch stops the upload. These checks do not establish printability; separate geometric and slicer validation reports cover that.

The first test uploaded `King_Shark_Catchall_Bowl_P1S_NON_AMS.3mf` (3,021,730 bytes). The returned SHA matched `98385e27e71b701dfe92d7879a692257d339ed26`. The complete first bowl batch contains 14 files totaling 19,226,634 bytes.

## Files and continuation

- `source/blob_upload_io.py`: local chunk reader, inventory/SHA calculator, and receipt recorder. It has no network or credential functionality.
- `blob_uploads.json`: successful uploaded objects, repository paths, local paths, sizes, Git SHAs, and SHA-256 hashes. Only entries verified against the remote SHA are added.
- Final repository staging root: `outputs/Character_Catchalls_and_Shelves_v1/repo` relative to the workspace.

Before the root agent commits, recompute the staged file hashes. Reuse previously uploaded objects by matching SHA, even if a staged path differs. Create the new tree using the current repository base tree so unrelated content remains. Create a commit with the current parent, then update the branch with the expected prior SHA; inspect a changed branch head before retrying. Do not force an unrelated branch change.

## Limits and open checks

The 3 MB, 4 MB and 38,339,220-byte Blender uploads succeeded with exact Git blob SHA matches. The largest tested file used roughly 51.1 million base64 characters. This is a verified example, not a claim about an untested connector maximum. Some receipts initially reference local validation JSON files; final staging may sanitize machine-specific paths, which changes their content SHA and requires a fresh upload.

