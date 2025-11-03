import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Basic health check
    const health = {
      status: 'healthy',
      service: 'frontend-efimero',
      timestamp: new Date().toISOString(),
      version: process.env.npm_package_version || '1.0.0',
      node_version: process.version,
      environment: process.env.NODE_ENV || 'development'
    };

    return NextResponse.json(health);
  } catch (error) {
    return NextResponse.json(
      {
        status: 'unhealthy',
        service: 'frontend-efimero',
        timestamp: new Date().toISOString(),
        error: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}