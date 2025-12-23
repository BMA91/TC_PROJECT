"use client";

import { useEffect, useMemo, useState } from "react";

const PAGE_SIZE = 7;

type TicketStatus = "Ouvert" | "En cours" | "Résolu";

interface Ticket {
  id: number;
  user: string;
  time: string;
  subject: string;
  type: string;
  rating: number;
  status: TicketStatus;
}

export default function TicketsPage() {
  const [search, setSearch] = useState<string>("");
  const [filter, setFilter] = useState<TicketStatus | "all">("all");
  const [page, setPage] = useState<number>(1);

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
      } catch {
        setError("Erreur lors du chargement des tickets");
      } finally {
        setLoading(false);
      }
    };

    fetchTickets();
  }, []);

  const filteredTickets = useMemo<Ticket[]>(() => {
    let result = tickets;

    if (search) {
      result = result.filter(
        (t) =>
          t.user.toLowerCase().includes(search.toLowerCase()) ||
          t.subject.toLowerCase().includes(search.toLowerCase())
      );
    }

    if (filter !== "all") {
      result = result.filter((t) => t.status === filter);
    }

    return result;
  }, [search, filter, tickets]);

  const totalPages = Math.ceil(filteredTickets.length / PAGE_SIZE);

  const paginatedTickets = filteredTickets.slice(
    (page - 1) * PAGE_SIZE,
    page * PAGE_SIZE
  );

  const statusStyle = (status: TicketStatus): string => {
    if (status === "Ouvert") return "bg-blue-100 text-blue-600";
    if (status === "En cours") return "bg-orange-100 text-orange-600";
    return "bg-green-100 text-green-600";
  };

  return (
    <div className="flex h-screen bg-slate-100">
      <aside className="w-60 bg-[#0a1f44] text-white p-6">
        <h1 className="text-xl font-semibold mb-10">Admin</h1>
        <nav className="space-y-2">
          <a
            className="block px-4 py-3 rounded-lg cursor-pointer"
            href="/adminsPages/dashboard"
          >
            Dashboard
          </a>
          <a
            className="block px-4 py-3 rounded-lg bg-white/15 font-medium cursor-pointer"
            href="/adminsPages/tickets"
          >
            Tickets
          </a>
          <a
            className="block px-4 py-3 rounded-lg cursor-pointer"
            href="/adminsPages/admisclient"
          >
            Clients
          </a>
          <a
            className="block px-4 py-3 rounded-lg cursor-pointer"
            href="/adminsPages/agents-admin"
          >
            Agents
          </a>
          <a className="block px-4 py-3 rounded-lg cursor-pointer">
            Paramètres
          </a>
        </nav>
      </aside>

      <main className="flex-1 p-8 overflow-auto">
        <header className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-slate-800">Bonjour</h2>

          <div className="flex gap-3">
            <input
              type="text"
              placeholder="Rechercher par nom ou sujet..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="px-4 py-2 rounded-lg border border-slate-300"
            />

            <select
              value={filter}
              onChange={(e) => {
                setFilter(e.target.value as TicketStatus | "all");
                setPage(1);
              }}
              className="px-4 py-2 rounded-lg border border-slate-300"
            >
              <option value="all">Appliquer un filtre</option>
              <option value="Ouvert">Ouvert</option>
              <option value="En cours">En cours</option>
              <option value="Résolu">Résolu</option>
            </select>
          </div>
        </header>

        <section className="bg-white rounded-2xl p-6 shadow-sm">
          {loading && (
            <p className="text-center text-slate-400 py-10">
              Chargement des tickets...
            </p>
          )}

          {error && <p className="text-center text-red-500 py-10">{error}</p>}

          {!loading && !error && (
            <table className="w-full border-collapse">
              <thead>
                <tr className="text-left text-slate-500">
                  <th className="pb-4">
                    <input type="checkbox" />
                  </th>
                  <th className="pb-4">Utilisateur</th>
                  <th className="pb-4">Temps</th>
                  <th className="pb-4">Sujet</th>
                  <th className="pb-4">Type du Ticket</th>
                  <th className="pb-4">Rating</th>
                  <th className="pb-4">État</th>
                </tr>
              </thead>

              <tbody>
                {paginatedTickets.map((ticket) => (
                  <tr key={ticket.id} className="border-t">
                    <td className="py-4">
                      <input type="checkbox" />
                    </td>

                    <td className="py-4 flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-blue-600 text-white flex items-center justify-center font-semibold">
                        {ticket.user.charAt(0)}
                      </div>
                      {ticket.user}
                    </td>

                    <td className="py-4">{ticket.time}</td>
                    <td className="py-4">{ticket.subject}</td>
                    <td className="py-4">{ticket.type}</td>

                    <td className="py-4">
                      {"★".repeat(ticket.rating)}
                      {"☆".repeat(5 - ticket.rating)}
                    </td>

                    <td className="py-4">
                      <span
                        className={`px-3 py-1 rounded-full text-sm font-medium ${statusStyle(
                          ticket.status
                        )}`}
                      >
                        {ticket.status}
                      </span>
                    </td>
                  </tr>
                ))}

                {paginatedTickets.length === 0 && (
                  <tr>
                    <td
                      colSpan={7}
                      className="py-10 text-center text-slate-400"
                    >
                      Aucun ticket trouvé
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </section>

        <footer className="flex justify-center items-center gap-6 mt-6">
          <button
            disabled={page === 1}
            onClick={() => setPage((p) => p - 1)}
            className="px-4 py-2 rounded-lg bg-blue-600 text-white disabled:bg-blue-300"
          >
            Précédent
          </button>

          <span className="text-slate-600">
            Page {page} / {totalPages || 1}
          </span>

          <button
            disabled={page === totalPages || totalPages === 0}
            onClick={() => setPage((p) => p + 1)}
            className="px-4 py-2 rounded-lg bg-blue-600 text-white disabled:bg-blue-300"
          >
            Suivant
          </button>
        </footer>
      </main>
    </div>
  );
}
