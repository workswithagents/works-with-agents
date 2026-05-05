// Works With Agents — C# SDK
// Reference implementations for all Agent OSI Model protocols.
// Zero dependencies beyond System.Net.Http. Copy-pasteable. CC BY 4.0.

using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace WorksWithAgents
{
    public static class WWA
    {
        public const string DefaultApi = "https://workswithagents.dev";
        private static readonly HttpClient Client = new HttpClient();

        private static async Task<JsonElement> Request(string method, string path, object? body = null)
        {
            var req = new HttpRequestMessage(new HttpMethod(method), $"{DefaultApi}{path}");
            if (body != null)
            {
                var json = JsonSerializer.Serialize(body);
                req.Content = new StringContent(json, Encoding.UTF8, "application/json");
            }
            var resp = await Client.SendAsync(req);
            var content = await resp.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<JsonElement>(content);
        }

        // ── Trust Score ──────────────────────────────────────────────

        public static Task<JsonElement> TrustGet(string agentId)
            => Request("GET", $"/v1/trust/{agentId}");

        public static Task<JsonElement> TrustReport(string agentId, double successRate, int pitfalls = 0, int skills = 0)
            => Request("POST", "/v1/trust/report", new
            {
                agent_id = agentId,
                success_rate = successRate,
                pitfalls_contributed = pitfalls,
                skills_published = skills
            });

        public static Task<JsonElement> TrustRate(string fromAgent, string toAgent, double rating)
            => Request("POST", "/v1/trust/rate", new
            {
                from_agent = fromAgent,
                to_agent = toAgent,
                rating
            });

        // ── Deployment Manifest ──────────────────────────────────────

        public static Task<JsonElement> FleetDeploy<T>(T manifest)
            => Request("POST", "/v1/fleets/deploy", manifest);

        public static Task<JsonElement> FleetStatus(string fleetId)
            => Request("GET", $"/v1/fleets/{fleetId}/status");

        // ── SLA Framework ────────────────────────────────────────────

        public static Task<JsonElement> SLAReport(string fleetId, string agentId, string actionId,
            double durationSeconds, bool success)
            => Request("POST", "/v1/sla/report", new
            {
                fleet_id = fleetId,
                agent_id = agentId,
                action_id = actionId,
                duration_seconds = durationSeconds,
                success
            });

        public static Task<JsonElement> SLAStatus(string fleetId)
            => Request("GET", $"/v1/sla/{fleetId}/status");

        // ── Identity Protocol ────────────────────────────────────────

        public static Task<JsonElement> IdentityRegister(string agentId, string publicKey)
            => Request("POST", "/v1/identity/register", new
            {
                agent_id = agentId,
                public_key = publicKey
            });

        public static Task<JsonElement> IdentityVerify(string agentId, object message, string signature)
            => Request("POST", "/v1/identity/verify", new
            {
                agent_id = agentId,
                message,
                signature
            });

        // ── Compliance-as-Code ───────────────────────────────────────

        public static Task<JsonElement> ComplianceValidate(string regulation, object action)
            => Request("POST", "/v1/compliance/validate", new
            {
                regulation,
                action
            });

        public static Task<JsonElement> CompliancePacks()
            => Request("GET", "/v1/compliance/packs");

        public static async Task<bool> SafeExecute(object action, params string[] regulations)
        {
            foreach (var reg in regulations)
            {
                var result = await ComplianceValidate(reg, action);
                if (result.TryGetProperty("passed", out var passed) && !passed.GetBoolean())
                    return false;
            }
            return true;
        }

        // ── Onboarding ───────────────────────────────────────────────

        public static Task<JsonElement> OnboardInterview(string name, string purpose,
            string[] capabilities, string[]? skills = null)
            => Request("POST", "/v1/onboard/interview", new
            {
                agent_name = name,
                purpose,
                capabilities,
                skills = skills ?? Array.Empty<string>()
            });

        public static Task<JsonElement> OnboardGenerate(string interviewId)
            => Request("POST", $"/v1/onboard/{interviewId}/generate");

        public static Task<JsonElement> OnboardCalibrate(string interviewId)
            => Request("POST", $"/v1/onboard/{interviewId}/calibrate");

        public static Task<JsonElement> OnboardRegister(string interviewId)
            => Request("POST", $"/v1/onboard/{interviewId}/register");

        // ── Health ───────────────────────────────────────────────────

        public static Task<JsonElement> Health()
            => Request("GET", "/v1/health");
    }
}
