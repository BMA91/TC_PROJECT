"use client";

import { useEffect, useMemo, useState, ChangeEvent } from "react";
import { useRouter } from "next/navigation";

interface Ticket {
  id: number;
  title: string;
  description: string;
  status: string;
  priority?: string;
  created_at?: string;
  comments_count?: number;
}

export default function DashboardPage() {
  const router = useRouter();

  const [search, setSearch] = useState<string>("");
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTickets = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/tickets/");
        if (!res.ok) throw new Error("Failed to fetch tickets");

        const data: Ticket[] = await res.json();
        setTickets(Array.isArray(data) ? data : []);
      } catch (err) {
        setError("Erreur lors du chargement des tickets");
      } finally {
        setLoading(false);
      }
    };

    fetchTickets();
  }, []);

  const handleSearch = (e: ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
  };

  const filteredTickets = useMemo(() => {
    if (!search) return tickets;
    return tickets.filter((t) =>
      t.title.toLowerCase().includes(search.toLowerCase())
    );
  }, [search, tickets]);

  const stats = {
    Nouveau: tickets.filter((t) => t.status === "Nouveau").length,
    "En progrès": tickets.filter((t) => t.status === "En progrès").length,
    "À inspecter": tickets.filter((t) => t.status === "À inspecter").length,
    Urgent: tickets.filter((t) => t.priority === "Urgent").length,
    Satisfait: tickets.filter((t) => t.priority === "Satisfait").length,
  };

  const navItems = [
    { label: "Dashboard", path: "/adminsPages/dashboard" },
    { label: "Tickets", path: "/adminsPages/tickets" },
    { label: "Clients", path: "/adminsPages/admisclient" },
    { label: "Agents", path: "/adminsPages/agents-admin" },
    { label: "Paramètres", path: "/adminsPages/settings" },
  ];

  return (
    <div className="flex h-screen bg-slate-100">
      <aside className="w-60 bg-[#0a1f44] text-white p-6">
        <h1 className="text-xl font-semibold mb-10">Admin</h1>
        <nav className="space-y-2">
          {navItems.map((item) => (
            <a
              key={item.label}
              onClick={() => router.push(item.path)}
              className="block px-4 py-3 rounded-lg bg-white/15 font-medium cursor-pointer hover:bg-white/25"
            >
              {item.label}
            </a>
          ))}
        </nav>
      </aside>

      <main className="flex-1 p-8 overflow-auto">
        <header className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-slate-800">Bonjour,</h2>
          <input
            type="text"
            placeholder="Rechercher..."
            value={search}
            onChange={handleSearch}
            className="px-4 py-2 rounded-lg border border-slate-300"
          />
        </header>

        <section className="grid grid-cols-5 gap-4 mb-8">
          {Object.entries(stats).map(([label, value]) => (
            <div
              key={label}
              className="bg-white rounded-xl p-4 border text-center"
            >
              <p className="text-sm text-slate-500">{label}</p>
              <p className="text-2xl font-semibold">{value}</p>
            </div>
          ))}
        </section>

        <section className="space-y-4">
          {loading && (
            <p className="text-center text-slate-400">
              Chargement des tickets...
            </p>
          )}
          {error && <p className="text-center text-red-500">{error}</p>}

          {!loading &&
            !error &&
            filteredTickets.map((ticket) => (
              <div
                key={ticket.id}
                className="bg-white rounded-xl p-5 border flex justify-between items-start"
              >
                <div className="border-l-4 border-blue-600 pl-4">
                  <h4 className="font-semibold">{ticket.title}</h4>
                  <p className="text-sm text-slate-500">{ticket.description}</p>
                </div>

                <div className="text-sm text-slate-500 text-right space-y-1">
                  <p>💬 {ticket.comments_count ?? 0} commentaires</p>
                  <p>
                    📅{" "}
                    {ticket.created_at
                      ? new Date(ticket.created_at).toLocaleDateString()
                      : "-"}
                  </p>
                  <span className="text-blue-600 font-medium">
                    {ticket.status}
                  </span>
                </div>
              </div>
            ))}

          {!loading && filteredTickets.length === 0 && (
            <p className="text-center text-slate-400">Aucun ticket trouvé</p>
          )}
        </section>
      </main>
    </div>
  );
}
