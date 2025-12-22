"use client";

import { useState, useContext, useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import { LoginContext } from "../../layout";
import Link from "next/link";
import Image from "next/image";
const logo = "/images/logo.svg";
const userp = "/images/user.svg";
export default function TicketsPage() {
  const context = useContext(LoginContext);
  const { loginData } = context ?? {};

  const PAGE_SIZE = 6;

  
  useEffect(() => {
    if (!loginData) {
      router.push("/auth");
    }
  }, [loginData, router]);

  if (!context) return null;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e) => {
    setFormData((prev) => ({ ...prev, attachment: e.target.files[0] }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log(formData);
  };

  useEffect(() => {
    if (!context?.loginData) {
      router.push("/auth");
    }
  }, [context?.loginData, router]);

  if (!context) return null;

const [menu, setMenu] = useState(false);
  const [formData, setFormData] = useState({
    ticketType: "",
    subject: "",
    description: "",
    attachment: null,
  });
  const mockTickets = [
    {
      id: 12365,
      type: "recherche",
      status: "done",
      rating: null,
      date: "2025-12-17",
    },
    {
      id: 12425,
      type: "innovation",
      status: "pending",
      rating: null,
      date: "2025-12-18",
    },
    {
      id: 12345,
      type: "design",
      status: "done",
      rating: 4,
      date: "2025-12-19",
    },
    {
      id: 12375,
      type: "promotion",
      status: "done",
      rating: 5,
      date: "2025-12-20",
    },
    {
      id: 12895,
      type: "recherche",
      status: "pending",
      rating: null,
      date: "2025-12-21",
    },
    {
      id: 19565,
      type: "création de contenu",
      status: "done",
      rating: 4,
      date: "2025-12-22",
    },
  ];
  const [tab, setTab] = useState("all");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [from, setFrom] = useState("2025-12-17");
  const [to, setTo] = useState("2025-12-23");
  const filteredTickets = useMemo(() => {
    return mockTickets
      .filter((t) => {
        if (tab === "pending") return t.status === "pending";
        if (tab === "done") return t.status === "done";
        return true;
      })
      .filter((t) => t.date >= from && t.date <= to)
      .filter(
        (t) =>
          t.type.toLowerCase().includes(search.toLowerCase()) ||
          String(t.id).includes(search)
      );
  }, [tab, search, from, to]);
  const totalPages = Math.ceil(filteredTickets.length / PAGE_SIZE);
  const paginatedTickets = filteredTickets.slice(
    (page - 1) * PAGE_SIZE,
    page * PAGE_SIZE
  );
  const router = useRouter();

  

  return (
    <main className="">
      <div className="bg-[#0C2155] h-10 w-full"></div>

      <nav className="px-6 py-4 flex items-center">
        <div className="flex items-center gap-2">
          <Image src={logo} alt="Doxa logo" width={32} height={32} />
          <span className="text-2xl font-bold text-blue-900">Doxa</span>
        </div>
        <div className="flex gap-8 ml-24">
          <a
            href="/dashboard"
            className="text-blue-900 font-medium hover:text-blue-700 transition"
          >
            Home
          </a>
          <a
            href="#"
            className="text-blue-900 font-medium hover:text-blue-700 transition"
          >
            À propos
          </a>
          <a
            href="#"
            className="text-blue-900 font-medium hover:text-blue-700 transition"
          >
            Tarification
          </a>
          <a
            href="#"
            className="text-blue-900 font-medium hover:text-blue-700 transition"
          >
            Aide
          </a>
        </div>
        <Link
          href="/dashboard/tickets"
          className="ml-auto bg-blue-600 px-6 py-2 text-white rounded-lg hover:bg-blue-700"
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
              <p className="text-[#AAC7FF] text-sm">UI/UX Designer</p>

              <hr className="my-3 border-white/30" />

              <button className="border border-white rounded px-2 py-1 mb-3">
                Modify
              </button>

              <hr className="my-3 border-white/30" />

              <div className="flex flex-col gap-2">
                <div className="flex items-center gap-2">
                  <img src="./s" alt="" />
                  <button>Notifications</button>
                </div>

                <div className="flex items-center gap-2">
                  <img src="./s" alt="" />
                  <button>Messages</button>
                </div>

                <hr className="my-2 border-white/30" />

                <div className="flex items-center gap-2">
                  <img src="./s" alt="" />
                  <button>Aide</button>
                </div>

                <div className="flex items-center gap-2">
                  <img src="./s" alt="" />
                  <button>Paramètres</button>
                </div>

                <hr className="my-2 border-white/30" />

                <button className="text-red-400 text-left">Logout</button>
              </div>
            </div>
          )}
        </div>
      </nav>
      <h1 className="text-3xl pt-5 pl-5 font-bold mb-6">Vos tickets</h1>
      <div>
        <div className="min-h-screen bg-[#f6fbfc] p-10">
          <h1 className="text-2xl font-semibold mb-6">
            Historique des tickets
          </h1>

          {/* Tabs & Filters */}
          <div className="flex flex-wrap items-center gap-4 mb-6">
            <div className="flex gap-6 text-sm font-medium">
              <button
                onClick={() => setTab("all")}
                className={tab === "all" ? "text-blue-600" : ""}
              >
                Tous les tickets
              </button>
              <button
                onClick={() => setTab("pending")}
                className={tab === "pending" ? "text-blue-600" : ""}
              >
                en attente
              </button>
              <button
                onClick={() => setTab("done")}
                className={tab === "done" ? "text-blue-600" : ""}
              >
                effectués
              </button>
            </div>

            <div className="ml-auto flex items-center gap-3">
              <input
                type="date"
                value={from}
                onChange={(e) => setFrom(e.target.value)}
                className="border rounded-md px-3 py-1 text-sm"
              />
              <span className="text-sm">au</span>
              <input
                type="date"
                value={to}
                onChange={(e) => setTo(e.target.value)}
                className="border rounded-md px-3 py-1 text-sm"
              />
              <button className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm">
                nouveau ticket
              </button>
            </div>
          </div>

          {/* Search */}
          <input
            placeholder="rechercher un ticket"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="mb-4 w-64 px-4 py-2 rounded-full border text-sm"
          />

          {/* Table */}
          <div className="bg-white rounded-lg overflow-hidden shadow-sm">
            <table className="w-full text-sm">
              <thead className="bg-blue-600 text-white">
                <tr>
                  <th className="p-3 text-left">ID</th>
                  <th className="p-3 text-left">Type</th>
                  <th className="p-3 text-left">Status</th>
                  <th className="p-3 text-center">Voir plus</th>
                  <th className="p-3 text-center">Rating</th>
                  <th className="p-3 text-center">Action</th>
                </tr>
              </thead>

              <tbody>
                {paginatedTickets.map((ticket) => (
                  <tr key={ticket.id} className="border-b">
                    <td className="p-3">#{ticket.id}</td>
                    <td className="p-3 capitalize">{ticket.type}</td>
                    <td className="p-3">
                      <span
                        className={`px-3 py-1 rounded-full text-xs ${
                          ticket.status === "done"
                            ? "bg-green-100 text-green-700"
                            : "bg-blue-100 text-blue-700"
                        }`}
                      >
                        {ticket.status === "done" ? "Fini" : "En cours"}
                      </span>
                    </td>
                    <td className="p-3 text-center">ⓘ</td>
                    <td className="p-3 text-center">
                      {ticket.rating ? (
                        "★".repeat(ticket.rating) +
                        "☆".repeat(5 - ticket.rating)
                      ) : (
                        <button className="border px-3 py-1 rounded-md text-xs">
                          + rating
                        </button>
                      )}
                    </td>
                    <td className="p-3 text-center">—</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex justify-center gap-2 mt-6 text-sm">
            <button
              disabled={page === 1}
              onClick={() => setPage((p) => p - 1)}
              className="px-3 py-1 disabled:opacity-50"
            >
              ← Previous
            </button>

            {Array.from({ length: totalPages }).map((_, i) => (
              <button
                key={i}
                onClick={() => setPage(i + 1)}
                className={`px-3 py-1 rounded ${
                  page === i + 1 ? "bg-black text-white" : ""
                }`}
              >
                {i + 1}
              </button>
            ))}

            <button
              disabled={page === totalPages}
              onClick={() => setPage((p) => p + 1)}
              className="px-3 py-1 disabled:opacity-50"
            >
              Next →
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}
