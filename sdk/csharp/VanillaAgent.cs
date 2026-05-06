// Vanilla Agent — C# reference implementation.
// Full 7-layer OSI Model. Single file. Zero dependencies beyond .NET stdlib.
// Copy, build, run. CC BY 4.0.
//
// Usage: dotnet run --project vanilla_agent.csproj -- --demo

using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace WorksWithAgents
{
    // ═════════════════════════════════════════════════════════════════
    // L2 — Identity Protocol
    // ═════════════════════════════════════════════════════════════════
    class AgentIdentity
    {
        public string AgentId { get; }
        public string PublicKeyHex { get; }

        public AgentIdentity(string agentId)
        {
            AgentId = agentId;
            var rng = RandomNumberGenerator.Create();
            var bytes = new byte[32]; rng.GetBytes(bytes);
            PublicKeyHex = BitConverter.ToString(SHA256.HashData(bytes)).Replace("-", "").ToLower();
        }

        public string Sign(Dictionary<string, object> payload)
        {
            var json = JsonSerializer.Serialize(payload);
            var data = Encoding.UTF8.GetBytes(json + PublicKeyHex);
            return BitConverter.ToString(SHA256.HashData(data)).Replace("-", "").ToLower();
        }

        public static bool Verify(string agentId, Dictionary<string, object> payload,
                                   string signature, string publicKey)
        {
            var json = JsonSerializer.Serialize(payload);
            var data = Encoding.UTF8.GetBytes(json + publicKey);
            return BitConverter.ToString(SHA256.HashData(data)).Replace("-", "").ToLower() == signature;
        }
    }

    // ═════════════════════════════════════════════════════════════════
    // L4 — Handoff Protocol
    // ═════════════════════════════════════════════════════════════════
    class HandoffProtocol
    {
        public Dictionary<string, object> CreateHandoff(string taskId, AgentIdentity sender,
            Dictionary<string, object> task, List<string> checklist = null)
        {
            var payload = new Dictionary<string, object>
            {
                ["handoff_id"] = Guid.NewGuid().ToString(),
                ["task_id"] = taskId,
                ["sender"] = new Dictionary<string, string> { ["agent_id"] = sender.AgentId },
                ["context"] = new Dictionary<string, object>
                {
                    ["task_description"] = task.GetValueOrDefault("description", ""),
                    ["quality_checklist"] = checklist ?? new List<string> { "Verify output", "Run tests" }
                }
            };
            (payload["sender"] as Dictionary<string, string>)["identity_sig"] = sender.Sign(payload);
            return payload;
        }

        public Dictionary<string, object> AcceptHandoff(Dictionary<string, object> handoff, AgentIdentity receiver)
        {
            return new Dictionary<string, object>
            {
                ["status"] = "accepted",
                ["handoff_id"] = handoff["handoff_id"],
                ["receiver"] = receiver.AgentId,
                ["estimated_completion"] = DateTime.UtcNow.ToString("O")
            };
        }
    }

    // ═════════════════════════════════════════════════════════════════
    // L5 — Coordination Protocol
    // ═════════════════════════════════════════════════════════════════
    enum AgentRole { Leader, Follower, Candidate }

    class CoordinationClient
    {
        public string AgentId { get; }
        public AgentRole Role { get; private set; } = AgentRole.Follower;
        public int Term { get; private set; }
        public string LeaderId { get; private set; }
        public List<string> Peers { get; set; } = new();
        private Dictionary<string, Dictionary<string, object>> WorkQueue = new();

        public CoordinationClient(string agentId) => AgentId = agentId;

        public Dictionary<string, object> StartElection()
        {
            Role = AgentRole.Candidate;
            Term++;
            return new() { ["type"] = "elect", ["candidate"] = AgentId, ["term"] = Term };
        }

        public Dictionary<string, object> BecomeLeader()
        {
            Role = AgentRole.Leader;
            LeaderId = AgentId;
            return new() { ["type"] = "heartbeat", ["leader"] = AgentId, ["term"] = Term };
        }

        public string AssignWork(string target, Dictionary<string, object> task, int priority = 5)
        {
            var tid = "task-" + Guid.NewGuid().ToString()[..8];
            WorkQueue[tid] = new() { ["target"] = target, ["task"] = task, ["priority"] = priority, ["status"] = "assigned" };
            return tid;
        }

        public Dictionary<string, object> GetStatus() => new()
        {
            ["role"] = Role.ToString().ToLower(), ["leader"] = LeaderId,
            ["term"] = Term, ["active_tasks"] = WorkQueue.Count
        };
    }

    // ═════════════════════════════════════════════════════════════════
    // L7 — Transaction Protocol
    // ═════════════════════════════════════════════════════════════════
    enum TxStatus { Intent, Completed, Failed, RolledBack }

    class Transaction
    {
        public string TxId { get; set; } = Guid.NewGuid().ToString();
        public string Intent { get; set; }
        public string AgentId { get; set; }
        public TxStatus Status { get; set; } = TxStatus.Intent;
        public string CreatedAt { get; set; } = DateTime.UtcNow.ToString("O");
        public string CompletedAt { get; set; }
        public object Result { get; set; }
        public string Error { get; set; }
    }

    class TransactionLedger
    {
        private readonly Dictionary<string, Transaction> ledger = new();

        public Transaction Intent(string description, string agentId)
        {
            var tx = new Transaction { Intent = description, AgentId = agentId };
            ledger[tx.TxId] = tx;
            return tx;
        }

        public Transaction Execute(Transaction tx, Func<object> fn)
        {
            try
            {
                tx.Result = fn();
                tx.Status = TxStatus.Completed;
                tx.CompletedAt = DateTime.UtcNow.ToString("O");
            }
            catch (Exception e)
            {
                tx.Status = TxStatus.Failed;
                tx.Error = e.Message;
            }
            return tx;
        }

        public List<Dictionary<string, object>> Audit() => ledger.Values.Select(tx =>
            new Dictionary<string, object> {
                ["id"] = tx.TxId, ["intent"] = tx.Intent,
                ["status"] = tx.Status.ToString(), ["error"] = tx.Error
            }).ToList();

        public Dictionary<string, object> Stats() => new()
        {
            ["total"] = ledger.Count,
            ["completed"] = ledger.Values.Count(t => t.Status == TxStatus.Completed),
            ["failed"] = ledger.Values.Count(t => t.Status == TxStatus.Failed)
        };
    }

    // ═════════════════════════════════════════════════════════════════
    // L7 — Compliance Gate
    // ═════════════════════════════════════════════════════════════════
    static class ComplianceGate
    {
        private static readonly Dictionary<string, List<(string field, string[] value, string message)>> Rules = new()
        {
            ["nhs_dtac"] = new() {
                ("data_classification", new[] { "patient_identifiable", "clinical_confidential" },
                 "Patient data must not be processed without DPIA")
            },
            ["gdpr"] = new() {
                ("data_classification", new[] { "personal_data_unconsented" },
                 "Unconsented personal data blocked")
            }
        };

        public static Dictionary<string, object> Validate(string regulation, Dictionary<string, object> action)
        {
            var violations = new List<string>();
            if (Rules.TryGetValue(regulation, out var rules))
            {
                foreach (var (field, values, message) in rules)
                {
                    var actual = action.GetValueOrDefault(field, "")?.ToString();
                    if (values.Contains(actual))
                        violations.Add(message);
                }
            }
            return new() { ["passed"] = violations.Count == 0, ["violations"] = violations };
        }
    }

    // ═════════════════════════════════════════════════════════════════
    // Vanilla Agent
    // ═════════════════════════════════════════════════════════════════
    class VanillaAgent
    {
        public string Name { get; }
        public string Purpose { get; }
        public string AgentId { get; }
        public List<string> Tools { get; }
        public AgentIdentity Identity { get; }
        public HandoffProtocol Handoff { get; } = new();
        public CoordinationClient Coord { get; }
        public TransactionLedger Ledger { get; }
        public readonly List<Dictionary<string, object>> HandoffQueue = new();
        public int TasksDone { get; private set; }
        public int TasksFailed { get; private set; }

        public VanillaAgent(string name, string purpose, List<string> tools = null)
        {
            Name = name; Purpose = purpose;
            Tools = tools ?? new() { "terminal", "file" };
            AgentId = $"agent-{name}-{Guid.NewGuid().ToString()[..6]}";
            Identity = new AgentIdentity(AgentId);
            Coord = new CoordinationClient(AgentId);
            Ledger = new TransactionLedger();
        }

        public Dictionary<string, object> Boot() => new()
        {
            ["agent_id"] = AgentId,
            ["identity"] = Identity.PublicKeyHex[..16] + "...",
            ["tools"] = Tools,
            ["status"] = "ready"
        };

        public Dictionary<string, object> ReceiveTask(Dictionary<string, object> task)
        {
            var handoff = Handoff.CreateHandoff(
                task.GetValueOrDefault("task_id", Guid.NewGuid().ToString())?.ToString(),
                Identity, task);
            var response = Handoff.AcceptHandoff(handoff, Identity);
            HandoffQueue.Add(new() { ["handoff"] = handoff, ["accepted"] = response["status"] });
            response["result"] = Execute(task);
            return response;
        }

        public Dictionary<string, object> Execute(Dictionary<string, object> task)
        {
            foreach (var regulation in new[] { "nhs_dtac", "gdpr" })
            {
                var result = ComplianceGate.Validate(regulation, task);
                if (!(bool)result["passed"])
                    return new() { ["status"] = "blocked", ["violations"] = result["violations"] };
            }

            var tx = Ledger.Intent(task.GetValueOrDefault("description", "execute task")?.ToString(), AgentId);
            Ledger.Execute(tx, () => { Console.WriteLine($"  [{AgentId}] Running {task.GetValueOrDefault("tool", "echo")}..."); return new { ok = true }; });

            if (tx.Status == TxStatus.Completed) { TasksDone++; return new() { ["status"] = "completed", ["tx_id"] = tx.TxId }; }
            TasksFailed++;
            return new() { ["status"] = "failed", ["error"] = tx.Error };
        }

        public Dictionary<string, object> JoinFleet(List<string> peers)
        {
            Coord.Peers = peers ?? new();
            Coord.StartElection();
            return Coord.GetStatus();
        }

        public Dictionary<string, object> Report() => new()
        {
            ["agent_id"] = AgentId, ["name"] = Name, ["purpose"] = Purpose,
            ["tools"] = Tools, ["tasks_done"] = TasksDone, ["tasks_failed"] = TasksFailed,
            ["handoffs_received"] = HandoffQueue.Count,
            ["coordination"] = Coord.GetStatus(), ["audit"] = Ledger.Stats()
        };
    }

    // ═════════════════════════════════════════════════════════════════
    // Demo
    // ═════════════════════════════════════════════════════════════════
    class Program
    {
        static void Main(string[] args)
        {
            bool demo = args.Contains("--demo");
            if (!demo) { Console.WriteLine("Vanilla Agent — C#. Use --demo for the OSI demo."); return; }

            Console.WriteLine(new string('═', 60));
            Console.WriteLine("  Vanilla Agent — OSI Reference (C#)");
            Console.WriteLine("  Works With Agents · CC BY 4.0");
            Console.WriteLine(new string('═', 60) + "\n");

            var builder = new VanillaAgent("builder", "build software", new() { "terminal", "file", "git" });
            var reviewer = new VanillaAgent("reviewer", "review code", new() { "terminal", "file", "web" });

            Console.WriteLine("── L1-L3: Boot, Identity, Capabilities ──");
            Console.WriteLine($"  {builder.Boot()["agent_id"]} ready");
            Console.WriteLine($"  {reviewer.Boot()["agent_id"]} ready\n");

            Console.WriteLine("── L4: Handoff Protocol ──");
            var task = new Dictionary<string, object> {
                ["task_id"] = "task-001", ["description"] = "Build API endpoint",
                ["tool"] = "file", ["data_classification"] = "internal"
            };
            var result = reviewer.ReceiveTask(task);
            Console.WriteLine($"  {reviewer.AgentId} received: {result["status"]}\n");

            Console.WriteLine("── L5: Coordination Protocol ──");
            var fleet = builder.JoinFleet(new() { reviewer.AgentId });
            Console.WriteLine($"  {builder.AgentId} fleet: {fleet["role"]} (term {fleet["term"]})");
            builder.Coord.AssignWork(reviewer.AgentId, new() { ["description"] = "Review PR", ["tool"] = "terminal" });
            Console.WriteLine($"  {builder.AgentId} assigned work to {reviewer.AgentId}\n");

            Console.WriteLine("── L6-L7: Execute + Governance ──");
            var safe = builder.Execute(new() { ["description"] = "Run tests", ["tool"] = "terminal", ["data_classification"] = "internal" });
            Console.WriteLine($"  Safe: {safe["status"]}");
            var blocked = builder.Execute(new() { ["description"] = "Process patient data", ["tool"] = "file", ["data_classification"] = "patient_identifiable" });
            Console.WriteLine($"  Blocked: {blocked["status"]}\n");

            Console.WriteLine("── L7: Audit Trail ──");
            foreach (var e in builder.Ledger.Audit())
                Console.WriteLine($"  [{e["status"]}] {e["intent"]}");
            Console.WriteLine();

            Console.WriteLine("── Reports ──");
            foreach (var a in new[] { builder, reviewer })
            {
                var r = a.Report();
                Console.WriteLine($"  {r["agent_id"]}: {r["tasks_done"]} done, {r["tasks_failed"]} failed");
            }
            Console.WriteLine("\n" + new string('═', 60));
            Console.WriteLine("  Demo complete. 7 layers, 2 agents, 0 external deps.");
            Console.WriteLine(new string('═', 60));
        }
    }
}
