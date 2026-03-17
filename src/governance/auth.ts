export class AuthManager {
  createToken(userId: string, roles: string[]): string {
    const payload = JSON.stringify({ userId, roles, createdAt: Date.now() });
    return Buffer.from(payload).toString('base64');
  }

  validateToken(token: string): { valid: boolean; userId?: string; roles?: string[] } {
    try {
      const payload = JSON.parse(Buffer.from(token, 'base64').toString('utf8'));
      if (payload.userId && Array.isArray(payload.roles)) {
        return { valid: true, userId: payload.userId, roles: payload.roles };
      }
      return { valid: false };
    } catch {
      return { valid: false };
    }
  }

  hasRole(token: string, role: string): boolean {
    const { valid, roles } = this.validateToken(token);
    return valid && (roles?.includes(role) ?? false);
  }

  hasPermission(token: string, permission: string, permissionMap: Record<string, string[]>): boolean {
    const { valid, roles } = this.validateToken(token);
    if (!valid || !roles) return false;
    return roles.some(role => permissionMap[role]?.includes(permission));
  }
}
