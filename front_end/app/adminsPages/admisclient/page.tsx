"use client";

import { useEffect, useMemo, useState, ChangeEvent } from "react";
import { useRouter } from "next/navigation";

const PAGE_SIZE = 6;

interface Client {
  id: number;
  nom?: string;
  prenom?: string;
  telephone?: string;
  email?: string;
  created_at?: string;
}

export default function ClientsPage() {
  const router = useRouter();

  const [search, setSearch] = useState<string>("");
  const [filter, setFilter] = useState<string>("all");
  const [page, setPage] = useState<number>(1);
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchClients = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/users/");
        if (!res.ok) throw new Error("Failed to fetch clients");
        const data: Client[] = await res.json();
        setClients(Array.isArray(data) ? data : []);
      } catch {
        setError("Erreur lors du chargement des clients");
      } finally {
        setLoading(false);
      }
    };

    fetchClients();
  }, []);

  const filteredClients = useMemo(() => {
    let result = clients;

    if (search) {
      const s = search.toLowerCase();
      result = result.filter((c) => {
        const fullName = `${c.nom || ""} ${c.prenom || ""}`.trim();
        return (
          fullName.toLowerCase().includes(s) ||
          (c.email || "").toLowerCase().includes(s)
        );
      });
    }

    if (filter !== "all") {
      result = result.filter((c) => (c.email || "").includes(filter));
    }

    return result;
  }, [search, filter, clients]);

  const totalPages = Math.ceil(filteredClients.length / PAGE_SIZE);

  const paginatedClients = filteredClients.slice(
    (page - 1) * PAGE_SIZE,
    page * PAGE_SIZE
  );

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
              className={`block px-4 py-3 rounded-lg cursor-pointer font-medium ${
                item.label === "Clients" ? "bg-white/15" : "hover:bg-white/25"
              }`}
            >
              {item.label}
            </a>
          ))}
        </nav>
      </aside>

      <main className="flex-1 p-8 overflow-auto">
        <header className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-slate-800">Bonjour</h2>

          <div className="flex gap-3">
            <input
              type="text"
              placeholder="Rechercher par nom ou email..."
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
                setFilter(e.target.value);
                setPage(1);
              }}
              className="px-4 py-2 rounded-lg border border-slate-300"
            >
              <option value="all">Appliquer un filtre</option>
              <option value="gmail">Gmail</option>
            </select>
          </div>
        </header>

        <section className="bg-white rounded-2xl p-6 shadow-sm">
          {loading ? (
            <p className="text-center py-10 text-slate-400">
              Chargement des clients...
            </p>
          ) : error ? (
            <p className="text-center py-10 text-red-500">{error}</p>
          ) : (
            <table className="w-full border-collapse">
              <thead>
                <tr className="text-left text-slate-500">
                  <th className="pb-4 font-medium">Utilisateur</th>
                  <th className="pb-4 font-medium">Date</th>
                  <th className="pb-4 font-medium">Téléphone</th>
                  <th className="pb-4 font-medium">Email</th>
                </tr>
              </thead>

              <tbody>
                {paginatedClients.map((client) => (
                  <tr key={client.id} className="border-t">
                    <td className="py-4 flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-blue-600 text-white flex items-center justify-center font-semibold">
                        {(client.nom || client.email || "?").charAt(0)}
                      </div>
                      {`${client.nom || ""} ${client.prenom || ""}`.trim() || client.email}
                    </td>
                    <td className="py-4">{client.created_at ? new Date(client.created_at).toLocaleDateString() : "-"}</td>
                    <td className="py-4">{client.telephone || "-"}</td>
                    <td className="py-4">{client.email}</td>
                  </tr>
                ))}

                {paginatedClients.length === 0 && (
                  <tr>
                    <td
                      colSpan={4}
                      className="py-10 text-center text-slate-400"
                    >
                      Aucun résultat trouvé
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
