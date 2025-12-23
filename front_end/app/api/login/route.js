import { NextResponse } from 'next/server';

// Backend API URL - adjust if your backend runs on a different port
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function POST(request) {
  try {
    const body = await request.json();
    const { address, password } = body;

    // Validate input
    if (!address || !password) {
      return NextResponse.json(
        { error: 'Email and password are required' },
        { status: 400 }
      );
    }

    // Call backend API
    const response = await fetch(`${BACKEND_URL}/users/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: address, // Map 'address' from frontend to 'email' for backend
        password: password,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      // Backend returned an error
      return NextResponse.json(
        { error: data.detail || 'Invalid email or password' },
        { status: response.status }
      );
    }

    // Success - return user data
    return NextResponse.json(
      { 
        success: true, 
        user: data 
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('Login API error:', error);
    return NextResponse.json(
      { error: 'Failed to connect to backend server' },
      { status: 500 }
    );
  }
}

