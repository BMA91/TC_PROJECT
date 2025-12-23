import { NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function POST(request) {
  try {
    const body = await request.json();
    const { address, password } = body;

    if (!address || !password) {
      return NextResponse.json(
        { error: "Email and password are required" },
        { status: 400 }
      );
    }

    const response = await fetch(`${BACKEND_URL}/users/verify`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: address,
        password: password,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(
        { error: data.detail || "Invalid email or password" },
        { status: response.status }
      );
    }

    return NextResponse.json(
      {
        success: true,
        user: data,
      },
      { status: 200 }
    );
  } catch (error) {
    console.error("Login API error:", error);
    return NextResponse.json(
      { error: "Failed to connect to backend server" },
      { status: 500 }
    );
  }
}
