import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function POST(request) {
  try {
    const url = new URL(request.url);
    const client_id = url.searchParams.get('client_id');
    if (!client_id) {
      return NextResponse.json({ error: 'client_id query parameter is required' }, { status: 400 });
    }

    const body = await request.json();

    const response = await fetch(`${BACKEND_URL}/tickets/?client_id=${client_id}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();

    // Forward the backend response (success or error) unchanged so the frontend
    // can inspect validation errors returned by the backend.
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Tickets API error:', error);
    return NextResponse.json({ error: 'Échec de la connexion au serveur. Veuillez réessayer.' }, { status: 500 });
  }
}
