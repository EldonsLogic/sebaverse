# F2 static remediation experiment —15 November2026

DEV-006; requirementsR054/R075/R078/R094/R097/R098. This experiment creates/inspects a test-only derived OCI artifact and authenticated Ubuntu candidate archives. It never starts the database, installs those packages or approves F2. The main pre-use gate remains unchanged and rejects official-only identities; a derived source must receive its own exact binding before future use.

## Changes and actual checks

Static builder accepts exactly the authored FROM/COPY/USER recipe and hashes, fetches/hashes immutable parent manifest/config, rejects ONBUILD hooks before build, then uses existing Docker build tools with no RUN and network disabled for build stages. The output is streamed/hash-checked OCI content with exact platform/config/parent-layer lineage; no image entrypoint is executed. Separate read-only layer inspection checks that only intended directories and the exact0755 stub change, and retains upstream entrypoint source as data. Scanning uses the default image/file catalogers including OS and Go-binary coverage. A summary can only say held_findings or scan_clean_not_preuse_approved.

Authenticated native transaction metadata records every installed companion's old/new version, trusted Ubuntu source/checksum and existing notice. A separate helper downloads exact versions, verifies archive hashes and reads copyright data without extracting executable files or running maintainer scripts. Downloaded_not_installed remains distinct from installed or rights-approved.

## Observed failures retained as failures

-43690540793 stopped before build:parser did not accept apt's empty trailing statusmarker. Corrected with a regression case; removals/new/unknown packages still reject.
-43690686721 accepted the complete signed transaction but downloader omitted the already observed libc6-i386 companion. Exact companion added with version/origin/checksum regression.
-43690796071 stopped before build:existing Docker driver could not export OCI. No image execution occurred.

The disposable runner now enables its existing containerd image store, as [documented by Docker](https://docs.docker.com/engine/storage/containerd/), only after confirming GitHub Actions context and no existing containers. It preserves other daemon configuration and records actual Docker/storage versions. No new builder container/tool package is installed; no user Mac Docker settings changed. The local Mac daemon was unavailable and no local image build is claimed.

Actual successful build/scan, entrypoint review and candidate-package notice outcomes must be appended from real CI artifacts. Lower OCI layers retain original gosu bytes; no whole-archive erasure or redistribution clearance claimed. Real PostgreSQL migration/authentication/readiness/cleanup still require full native/image/core closure.

## Actual first successful experiment

Run43690950105 at32d666c completed successfully. Actual derived manifest:sha256:62b638d968c3d89ed09f8de2220edbe7029a9166cf2c1c7683727140be92db5a; OCIarchiveSHA256:a32f108521c466d9ec3b14c632bf37f0afafdba5e6f0e6c1f9d77026a0221c37. Full default image scan cataloged46 packages and reported3Medium matches, noHigh/Critical/Unknown. Summary explicitly says held_findings and phase_approval:false. No database or patch installation occurred. This clears neither native-system nor suppliercore findings and does not bind the current official-only runtime gate to the derivative.

Actual OCI hash/config/lineage and exactCOPYdelta checks passed; entrypoint source was retained as data. The116.7MB artifact download was slow, so a compact metadata/notices artifact was added for subsequent review; the full payload remains available in the originating run. Do not infer manual entrypoint review from successful extraction.

Local root checks after helper/parser fixes:106 foundation/policy/helper tests pass,83 backend tests pass (realPGcase deselected), Django0issues, dependencycheckerpass. Independent reviewer ran17 image/filesystem +13 nativehelper tests successfully and found no blocker in the bounded static experiment.
