"use client";

import { useState, useContext, useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import { LoginContext } from "../../layout";
import Link from "next/link";
import Image from "next/image";

const logo = "/images/logo.svg";
const userp = "/images/user.svg";
const PAGE_SIZE = 6;

export default function TicketsPage() {
  const context = useContext(LoginContext);
  const { loginData, setLoginData } = context ?? {};
  const router = useRouter();

  const [menu, setMenu] = useState(false);
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);

  const [tab, setTab] = useState("all");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [from, setFrom] = useState("2025-12-17");
  const [to, setTo] = useState("2025-12-23");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/tickets/")
      .then((res) => res.json())
      .then((data) => {
        setTickets(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch tickets:", err);
        setLoading(false);
      });
  }, [loginData, router]);

  const filteredTickets = useMemo(() => {
    return tickets
      .filter((t) =>
        tab === "pending"
          ? t.status === "pending"
          : tab === "done"
          ? t.status === "done"
          : true
      )
      .filter((t) => t.date >= from && t.date <= to)
      .filter(
        (t) =>
          t.type.toLowerCase().includes(search.toLowerCase()) ||
          String(t.id).includes(search)
      );
  }, [tickets, tab, search, from, to]);

  const totalPages = Math.ceil(filteredTickets.length / PAGE_SIZE);
  const paginatedTickets = filteredTickets.slice(
    (page - 1) * PAGE_SIZE,
    page * PAGE_SIZE
  );

  if (!context) return null;

  return (
    <main>
      <div className="bg-[#0C2155] h-10 w-full"></div>

      <nav className="px-6 py-4 flex items-center">
        <div className="flex items-center gap-2">
          <Image src={logo} alt="Doxa logo" width={32} height={32} />
          <span className="text-2xl font-bold text-blue-900">Doxa</span>
        </div>

        <div className="flex gap-8 ml-24">
          <Link href="/dashboard" className="nav-link">
            Home
          </Link>
          <Link href="#" className="nav-link">
            À propos
          </Link>
          <Link href="#" className="nav-link">
            Tarification
          </Link>
          <Link href="#" className="nav-link">
            Aide
          </Link>
        </div>

        <Link
          href="/dashboard/tickets"
          className="ml-auto bg-blue-600 px-6 py-2 text-white rounded-lg"
        >
          Vos tickets
        </Link>

        <div className="relative pl-6">
          <button
            onClick={() => setMenu(!menu)}
            className="flex items-center gap-2"
          >
            <Image src={userp} alt="Profile" width={32} height={32} />
            Profile
          </button>

          {menu && (
            <div className="absolute right-0 mt-3 w-56 bg-[#0C2155] text-white p-4 rounded-xl">
              <p className="font-semibold">{loginData?.address ?? "User"}</p>
              <p className="text-[#AAC7FF] text-sm">{loginData?.role ?? "User"}</p>
              <hr className="my-3 border-white/30" />
              <button className="border border-white rounded px-2 py-1 mb-3">
                Modify
              </button>
              <hr className="my-3 border-white/30" />
              <button
                onClick={() => {
                  try {
                    localStorage.removeItem("isAuth");
                    localStorage.removeItem("userData");
                  } catch (e) {}
                  setLoginData?.(null);
                  router.push("/auth");
                }}
                className="text-red-400 text-left"
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </nav>

      <h1 className="text-3xl pt-5 pl-5 font-bold">Vos tickets</h1>

      <div className="min-h-screen bg-[#f6fbfc] p-10">
        <h2 className="text-2xl font-semibold mb-6">Historique des tickets</h2>

        <div className="flex items-center gap-4 mb-6">
          <div className="flex gap-6 text-sm font-medium">
            <button
              onClick={() => setTab("all")}
              className={tab === "all" ? "text-blue-600" : ""}
            >
              Tous
            </button>
            <button
              onClick={() => setTab("pending")}
              className={tab === "pending" ? "text-blue-600" : ""}
            >
              En attente
            </button>
            <button
              onClick={() => setTab("done")}
              className={tab === "done" ? "text-blue-600" : ""}
            >
              Effectués
            </button>
          </div>

          <div className="ml-auto flex gap-3">
            <input
              type="date"
              value={from}
              onChange={(e) => setFrom(e.target.value)}
            />
            <input
              type="date"
              value={to}
              onChange={(e) => setTo(e.target.value)}
            />
          </div>
        </div>

        <input
          placeholder="Rechercher un ticket"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="mb-4 w-64 px-4 py-2 rounded-full border"
        />

        <div className="bg-white rounded-lg shadow-sm">
          {loading ? (
            <p className="p-6">Chargement des tickets...</p>
          ) : (
            <table className="w-full text-sm">
              <thead className="bg-blue-600 text-white">
                <tr>
                  <th className="p-3 text-left">ID</th>
                  <th className="p-3 text-left">Type</th>
                  <th className="p-3 text-left">Status</th>
                  <th className="p-3 text-center">Rating</th>
                </tr>
              </thead>
              <tbody>
                {paginatedTickets.map((ticket) => (
                  <tr key={ticket.id} className="border-b">
                    <td className="p-3">#{ticket.id}</td>
                    <td className="p-3 capitalize">{ticket.type}</td>
                    <td className="p-3">{ticket.status}</td>
                    <td className="p-3 text-center">
                      {ticket.rating
                        ? "★".repeat(ticket.rating) +
                          "☆".repeat(5 - ticket.rating)
                        : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="flex justify-center gap-2 mt-6">
          <button disabled={page === 1} onClick={() => setPage((p) => p - 1)}>
            ←
          </button>
          {Array.from({ length: totalPages }).map((_, i) => (
            <button
              key={i}
              onClick={() => setPage(i + 1)}
              className={page === i + 1 ? "font-bold" : ""}
            >
              {i + 1}
            </button>
          ))}
          <button
            disabled={page === totalPages}
            onClick={() => setPage((p) => p + 1)}
          >
            →
          </button>
        </div>
      </div>
    </main>
  );
}
