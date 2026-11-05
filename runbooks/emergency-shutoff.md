# Emergency shut-off of public exposure

| Value | This lab |
|---|---|
| Connector | cloudflared container on poseidon |
| Tunnel config | Remotely managed in Cloudflare Zero Trust |
| Inbound port forwards | None, so the tunnel is the only way in |

Use this when something published through the tunnel is under attack or may
be compromised. Each step works on its own. The fastest come first.

| Step | How | Effect | Undo |
|---|---|---|---|
| A. Stop the connector | poseidon webGUI, **Docker** tab, stop the cloudflared container. Needs LAN or VPN access | Every tunnel hostname goes down within seconds | Start the container |
| B. Remove the ingress | **Zero Trust > Networks > Tunnels > (tunnel) > Public hostnames**: delete the hostname for each app to cut, or all of them. Deleting one also removes its DNS record. The catch-all 404 stays | That app's hostname stops resolving. Works from anywhere you can reach the dashboard, and can cut one app at a time | Re-add each hostname with its service and TLS settings |
| C. Put everything behind Access | Add a self-hosted Access application covering every hostname on the domain, with the policy that allows only me | Only you can reach anything. Useful when you still need the services | Delete the application |
| D. Under Attack mode | Zone **Overview > Under Attack mode** | Every visitor gets a challenge. Use against floods | Turn it off |

Step A was rehearsed on 2026-11-05: every published app went offline within
seconds, the tunnel showed as down, and starting the container brought it
all back.

## Afterwards

1. Rotate the tunnel token if the connector or its host may be compromised,
   and update the cloudflared container with the new one.
2. Check the Access logs in Cloudflare and Traefik's access log on poseidon.
3. Record what happened, what you changed and when, and undo the steps you no
   longer need.
