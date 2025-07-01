/**
 * Health check utilities for development environment
 */

interface HealthCheckResult {
  service: string;
  status: 'healthy' | 'unhealthy' | 'unknown';
  url: string;
  error?: string;
  responseTime?: number;
}

export class HealthChecker {
  private static readonly BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  
  /**
   * Check if backend API is healthy
   */
  static async checkBackend(): Promise<HealthCheckResult> {
    const url = `${this.BACKEND_URL}/api/v1/health`;
    const startTime = Date.now();
    
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        // Short timeout for health checks
        signal: AbortSignal.timeout(5000)
      });
      
      const responseTime = Date.now() - startTime;
      
      if (response.ok) {
        return {
          service: 'Backend API',
          status: 'healthy',
          url,
          responseTime
        };
      } else {
        return {
          service: 'Backend API',
          status: 'unhealthy',
          url,
          error: `HTTP ${response.status}: ${response.statusText}`,
          responseTime
        };
      }
    } catch (error) {
      const responseTime = Date.now() - startTime;
      
      return {
        service: 'Backend API',
        status: 'unhealthy',
        url,
        error: error instanceof Error ? error.message : String(error),
        responseTime
      };
    }
  }
  
  /**
   * Check all services health
   */
  static async checkAllServices(): Promise<HealthCheckResult[]> {
    const results = await Promise.allSettled([
      this.checkBackend()
    ]);
    
    return results.map(result => 
      result.status === 'fulfilled' 
        ? result.value 
        : {
            service: 'Unknown',
            status: 'unknown' as const,
            url: '',
            error: 'Health check failed'
          }
    );
  }
  
  /**
   * Log health check results to console
   */
  static logHealthStatus(results: HealthCheckResult[]): void {
    console.group('🏥 System Health Check');
    
    results.forEach(result => {
      const icon = result.status === 'healthy' ? '✅' : 
                   result.status === 'unhealthy' ? '❌' : '❓';
      
      console.log(`${icon} ${result.service}: ${result.status.toUpperCase()}`);
      console.log(`   URL: ${result.url}`);
      
      if (result.responseTime) {
        console.log(`   Response Time: ${result.responseTime}ms`);
      }
      
      if (result.error) {
        console.log(`   Error: ${result.error}`);
      }
      
      console.log(''); // Empty line for readability
    });
    
    console.groupEnd();
  }
  
  /**
   * Run health check and log results (useful for development)
   */
  static async runDiagnostics(): Promise<boolean> {
    const results = await this.checkAllServices();
    this.logHealthStatus(results);
    
    // Return true if all services are healthy
    return results.every(result => result.status === 'healthy');
  }
}

// Auto-run health check in development
if (process.env.NODE_ENV === 'development' && typeof window !== 'undefined') {
  // Run health check after a short delay to allow services to start
  setTimeout(() => {
    HealthChecker.runDiagnostics().then(allHealthy => {
      if (!allHealthy) {
        console.warn('⚠️ Some services are not healthy. Check the logs above for details.');
      }
    });
  }, 2000);
}