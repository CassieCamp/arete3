import {
  MEMBER_NAVIGATION,
  COACH_NAVIGATION,
  ADMIN_NAVIGATION,
  MEMBER_MENU_NAVIGATION,
  COACH_MENU_NAVIGATION,
  ADMIN_MENU_NAVIGATION,
  getMainNavigationForRole,
  getMenuNavigationForRole
} from '../navigation';

describe('Navigation Role Separation', () => {
  describe('Member Navigation', () => {
    it('should contain only expected navigation items for members', () => {
      const expectedIds = ['journey', 'basecamp', 'compass'];
      const actualIds = MEMBER_NAVIGATION.map(item => item.id);
      
      expect(actualIds).toEqual(expect.arrayContaining(expectedIds));
      expect(actualIds).toHaveLength(expectedIds.length);
    });

    it('should not contain coach-specific navigation items', () => {
      const coachOnlyIds = ['practice', 'clients', 'profile'];
      const memberIds = MEMBER_NAVIGATION.map(item => item.id);
      
      coachOnlyIds.forEach(coachId => {
        expect(memberIds).not.toContain(coachId);
      });
    });

    it('should not contain admin-specific navigation items', () => {
      const adminOnlyIds = ['organizations'];
      const memberIds = MEMBER_NAVIGATION.map(item => item.id);
      
      adminOnlyIds.forEach(adminId => {
        expect(memberIds).not.toContain(adminId);
      });
    });

    it('should have correct hrefs for member navigation', () => {
      const memberNavigation = MEMBER_NAVIGATION;
      
      expect(memberNavigation.find(item => item.id === 'journey')?.href).toBe('/member/journey');
      expect(memberNavigation.find(item => item.id === 'basecamp')?.href).toBe('/member/center');
      expect(memberNavigation.find(item => item.id === 'compass')?.href).toBe('/member/coaching');
    });
  });

  describe('Coach Navigation', () => {
    it('should contain only expected navigation items for coaches', () => {
      const expectedIds = ['practice', 'clients', 'profile'];
      const actualIds = COACH_NAVIGATION.map(item => item.id);
      
      expect(actualIds).toEqual(expect.arrayContaining(expectedIds));
      expect(actualIds).toHaveLength(expectedIds.length);
    });

    it('should not contain member-specific navigation items', () => {
      const memberOnlyIds = ['journey', 'basecamp', 'compass'];
      const coachIds = COACH_NAVIGATION.map(item => item.id);
      
      memberOnlyIds.forEach(memberId => {
        expect(coachIds).not.toContain(memberId);
      });
    });

    it('should not contain admin-specific navigation items', () => {
      const adminOnlyIds = ['organizations'];
      const coachIds = COACH_NAVIGATION.map(item => item.id);
      
      adminOnlyIds.forEach(adminId => {
        expect(coachIds).not.toContain(adminId);
      });
    });

    it('should have correct hrefs for coach navigation', () => {
      const coachNavigation = COACH_NAVIGATION;
      
      expect(coachNavigation.find(item => item.id === 'practice')?.href).toBe('/coach/practice');
      expect(coachNavigation.find(item => item.id === 'clients')?.href).toBe('/coach/clients');
      expect(coachNavigation.find(item => item.id === 'profile')?.href).toBe('/coach/profile');
    });
  });

  describe('Admin Navigation', () => {
    it('should contain only expected navigation items for admins', () => {
      const expectedIds = ['organizations'];
      const actualIds = ADMIN_NAVIGATION.map(item => item.id);
      
      expect(actualIds).toEqual(expect.arrayContaining(expectedIds));
      expect(actualIds).toHaveLength(expectedIds.length);
    });

    it('should have correct hrefs for admin navigation', () => {
      const adminNavigation = ADMIN_NAVIGATION;
      
      expect(adminNavigation.find(item => item.id === 'organizations')?.href).toBe('/organizations');
    });
  });

  describe('Menu Navigation Role Separation', () => {
    it('should provide consistent menu navigation across roles', () => {
      const expectedMenuIds = ['profile', 'settings'];
      
      // All roles should have the same menu structure for now
      expect(MEMBER_MENU_NAVIGATION.map(item => item.id)).toEqual(expectedMenuIds);
      expect(COACH_MENU_NAVIGATION.map(item => item.id)).toEqual(expectedMenuIds);
      expect(ADMIN_MENU_NAVIGATION.map(item => item.id)).toEqual(expectedMenuIds);
    });
  });

  describe('Role-Based Navigation Getters', () => {
    it('should return correct navigation for member role', () => {
      const navigation = getMainNavigationForRole('member');
      const expectedIds = ['journey', 'basecamp', 'compass'];
      
      expect(navigation.map(item => item.id)).toEqual(expect.arrayContaining(expectedIds));
      expect(navigation).toHaveLength(expectedIds.length);
    });

    it('should return correct navigation for coach role', () => {
      const navigation = getMainNavigationForRole('coach');
      const expectedIds = ['practice', 'clients', 'profile'];
      
      expect(navigation.map(item => item.id)).toEqual(expect.arrayContaining(expectedIds));
      expect(navigation).toHaveLength(expectedIds.length);
    });

    it('should return correct navigation for admin role', () => {
      const navigation = getMainNavigationForRole('admin');
      const expectedIds = ['organizations'];
      
      expect(navigation.map(item => item.id)).toEqual(expect.arrayContaining(expectedIds));
      expect(navigation).toHaveLength(expectedIds.length);
    });

    it('should return empty array for unknown role', () => {
      // @ts-expect-error Testing invalid role
      const navigation = getMainNavigationForRole('unknown');
      expect(navigation).toEqual([]);
    });

    it('should return correct menu navigation for each role', () => {
      const memberMenu = getMenuNavigationForRole('member');
      const coachMenu = getMenuNavigationForRole('coach');
      const adminMenu = getMenuNavigationForRole('admin');
      
      const expectedMenuIds = ['profile', 'settings'];
      
      expect(memberMenu.map(item => item.id)).toEqual(expectedMenuIds);
      expect(coachMenu.map(item => item.id)).toEqual(expectedMenuIds);
      expect(adminMenu.map(item => item.id)).toEqual(expectedMenuIds);
    });
  });

  describe('Navigation Item Structure', () => {
    it('should have required properties for all navigation items', () => {
      const allNavigationItems = [
        ...MEMBER_NAVIGATION,
        ...COACH_NAVIGATION,
        ...ADMIN_NAVIGATION
      ];

      allNavigationItems.forEach(item => {
        expect(item).toHaveProperty('id');
        expect(item).toHaveProperty('icon');
        expect(item).toHaveProperty('label');
        expect(item).toHaveProperty('description');
        expect(typeof item.id).toBe('string');
        expect(typeof item.label).toBe('string');
        expect(typeof item.description).toBe('string');
        expect(item.icon).toBeDefined();
      });
    });

    it('should have required properties for all menu navigation items', () => {
      const allMenuItems = [
        ...MEMBER_MENU_NAVIGATION,
        ...COACH_MENU_NAVIGATION,
        ...ADMIN_MENU_NAVIGATION
      ];

      allMenuItems.forEach(item => {
        expect(item).toHaveProperty('id');
        expect(item).toHaveProperty('icon');
        expect(item).toHaveProperty('label');
        expect(item).toHaveProperty('href');
        expect(typeof item.id).toBe('string');
        expect(typeof item.label).toBe('string');
        expect(typeof item.href).toBe('string');
        expect(item.icon).toBeDefined();
      });
    });
  });

  describe('Role Isolation Verification', () => {
    it('should ensure no navigation item appears in multiple role arrays', () => {
      const memberIds = new Set(MEMBER_NAVIGATION.map(item => item.id));
      const coachIds = new Set(COACH_NAVIGATION.map(item => item.id));
      const adminIds = new Set(ADMIN_NAVIGATION.map(item => item.id));

      // Check for overlaps between member and coach
      const memberCoachOverlap = [...memberIds].filter(id => coachIds.has(id));
      expect(memberCoachOverlap).toEqual([]);

      // Check for overlaps between member and admin
      const memberAdminOverlap = [...memberIds].filter(id => adminIds.has(id));
      expect(memberAdminOverlap).toEqual([]);

      // Check for overlaps between coach and admin
      const coachAdminOverlap = [...coachIds].filter(id => adminIds.has(id));
      expect(coachAdminOverlap).toEqual([]);
    });
  });

  describe('Regression Prevention', () => {
    it('should prevent Profile tab from appearing in member navigation', () => {
      const memberIds = MEMBER_NAVIGATION.map(item => item.id);
      expect(memberIds).not.toContain('profile');
    });

    it('should ensure Profile tab only appears in coach navigation', () => {
      const coachIds = COACH_NAVIGATION.map(item => item.id);
      const memberIds = MEMBER_NAVIGATION.map(item => item.id);
      const adminIds = ADMIN_NAVIGATION.map(item => item.id);

      expect(coachIds).toContain('profile');
      expect(memberIds).not.toContain('profile');
      expect(adminIds).not.toContain('profile');
    });

    it('should ensure member-specific tabs do not appear in coach navigation', () => {
      const coachIds = COACH_NAVIGATION.map(item => item.id);
      const memberSpecificIds = ['journey', 'basecamp', 'compass'];

      memberSpecificIds.forEach(memberId => {
        expect(coachIds).not.toContain(memberId);
      });
    });

    it('should ensure coach-specific tabs do not appear in member navigation', () => {
      const memberIds = MEMBER_NAVIGATION.map(item => item.id);
      const coachSpecificIds = ['practice', 'clients'];

      coachSpecificIds.forEach(coachId => {
        expect(memberIds).not.toContain(coachId);
      });
    });
  });
});