# Static test-only derivation. No RUN and no base-image execution during build.
# Parent: official PostgreSQL17.12-alpine3.24 linux/amd64 platform manifest.
FROM docker.io/library/postgres@sha256:005c5c37db96c1e6652a79ea31f9886402fba81ac95dc2db897739121dd7f8f2
COPY --chmod=0755 gosu-disabled.sh /usr/local/bin/gosu
USER postgres
