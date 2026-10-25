import { createServerFn } from "@tanstack/react-start";
import { authMiddleware } from "@/lib/auth/middleware";
import { getSql } from "@/lib/db";

export type MembershipRow = {
  tenant_id: string;
  name: string;
  data_class: string;
  role: string;
};

const ROLE_LABEL: Record<string, string> = {
  platform_admin: "Plattform-Admin",
  tenant_admin: "Mandanten-Admin",
  therapist: "Therapeut",
  assistant: "Assistenz",
  client: "Klient",
};

export function roleLabel(role: string) {
  return ROLE_LABEL[role] ?? role;
}

export const listMemberships = createServerFn({ method: "GET" })
  .middleware([authMiddleware])
  .handler(async ({ context }) => {
    const sql = await getSql();
    return sql<MembershipRow>`
      select t.id as tenant_id, t.name, t.data_class, m.role
      from memberships m
      join tenants t on t.id = m.tenant_id
      where m.user_id = ${context.userId}
      order by m.created_at asc
    `;
  });

export const ensurePrimaryTenant = createServerFn({ method: "POST" })
  .middleware([authMiddleware])
  .handler(async ({ context }) => {
    const sql = await getSql();
    const existing = await sql<MembershipRow>`
      select t.id as tenant_id, t.name, t.data_class, m.role
      from memberships m
      join tenants t on t.id = m.tenant_id
      where m.user_id = ${context.userId}
      order by m.created_at asc
    `;
    if (existing.length > 0) return existing;

    const id = crypto.randomUUID();
    await sql`
      insert into tenants (id, name, data_class)
      values (${id}, ${"Erste Praxis"}, ${"synthetic"})
    `;
    await sql`
      insert into memberships (user_id, tenant_id, role)
      values (${context.userId}, ${id}, ${"tenant_admin"})
    `;
    return [
      {
        tenant_id: id,
        name: "Erste Praxis",
        data_class: "synthetic",
        role: "tenant_admin",
      },
    ] satisfies MembershipRow[];
  });

export const addSecondTenant = createServerFn({ method: "POST" })
  .middleware([authMiddleware])
  .handler(async ({ context }) => {
    const sql = await getSql();
    const count = await sql<{ n: number }>`
      select count(*)::int as n from memberships where user_id = ${context.userId}
    `;
    if ((count[0]?.n ?? 0) >= 2) {
      return sql<MembershipRow>`
        select t.id as tenant_id, t.name, t.data_class, m.role
        from memberships m
        join tenants t on t.id = m.tenant_id
        where m.user_id = ${context.userId}
        order by m.created_at asc
      `;
    }
    const id = crypto.randomUUID();
    await sql`
      insert into tenants (id, name, data_class)
      values (${id}, ${"Zweite Praxis"}, ${"synthetic"})
    `;
    await sql`
      insert into memberships (user_id, tenant_id, role)
      values (${context.userId}, ${id}, ${"tenant_admin"})
    `;
    return sql<MembershipRow>`
      select t.id as tenant_id, t.name, t.data_class, m.role
      from memberships m
      join tenants t on t.id = m.tenant_id
      where m.user_id = ${context.userId}
      order by m.created_at asc
    `;
  });
