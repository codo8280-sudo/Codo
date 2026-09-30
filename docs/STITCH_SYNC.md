# Stitch Synchronization

Project URL: https://stitch.withgoogle.com/projects/662663143724818153
Project ID: 662663143724818153

The project should be treated as a visual source of truth together with `DESIGN.md`.

## Secure access
Use `STITCH_API_KEY` from the environment. Never store the key in source control.

## Intended verification flow
1. List project screens through Stitch MCP.
2. Export or inspect every screen and its metadata.
3. Compare colors, typography, spacing, radius and responsive behavior with `DESIGN.md`.
4. Apply screen-by-screen Flutter implementation.
5. Run visual regression after each screen family.

This environment could not reach the Stitch MCP endpoint during this increment, and the shared URL redirected to Google Sign-In. No design details were invented beyond the project master DESIGN file.
