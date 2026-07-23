export type FormType =
  | "text"
  | "select"
  | "multiple"
  | "radio"
  | "date"
  | "boolean"
  | "number";

export type Role = "user" | "seller" | "admin" | "superadmin";

export type UserStatus =
  | "active"
  | "suspended"
  | "terminated"
  | "hibernating"
  | "under_review";

export type StoreStatus =
  | "active"
  | "suspended"
  | "terminated"
  | "hibernating"
  | "under_review"
  | "deactivated";

export type OrderStatus =
  | "pending"
  | "processing"
  | "shipped"
  | "delivered"
  | "cancelled"
  | "refunded"
  | "failed";

export type Condition = "brand new" | "used";

/* ── fastapi-pagination Page wrapper ─────────────────────────── */

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

/* ── Auth / User ─────────────────────────────────────────────── */

export interface User {
  id: number;
  fullname: string;
  email: string;
  email_verified: boolean;
  role: Role;
  status: UserStatus;
}

export interface Session {
  id: number;
  location: string | null;
  ip_address: string | null;
  device: string | null;
  expired_at: string;
  created_at: string;
}

export interface UserWithDetails extends User {
  stores?: Store[];
  sessions?: Session[];
}

/* ── Address ─────────────────────────────────────────────────── */

export interface Address {
  address_id: string;
  state: string;
  city: string;
  landmark: string | null;
  line_1: string;
  line_2: string | null;
  zip_code: number;
}

export interface AddressIn {
  state: string;
  city: string;
  landmark?: string | null;
  line_1: string;
  line_2?: string | null;
  zip_code: number;
}

/* ── Category / Attribute ────────────────────────────────────── */

export interface AttributeKey {
  id: number;
  name: string;
  required: boolean;
  form_type: FormType;
  options: string[] | null;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  sub_categories?: Category[];
}

export interface CategoryWithId extends Category {
  id: number;
  attributes?: AttributeKey[];
  sub_categories: CategoryWithId[];
}

export interface AdminCategory extends CategoryWithId {
  attributes: AttributeKey[];
  sub_categories: AdminCategory[];
}

/* ── Product ─────────────────────────────────────────────────── */

export interface Image {
  src: string;
  alt: string | null;
  name?: string;
}

export interface ProductAttribute {
  name: string;
  type: string;
  value: string | number | boolean | string[];
}

export interface Product {
  name: string;
  price: string;
  description: string;
  condition: Condition;
  available: boolean;
  slug: string;
  images: Image[];
}

export interface ProductDetail extends Product {
  category: { name: string; slug: string };
  attributes: ProductAttribute[];
}

/* ── Store ────────────────────────────────────────────────────── */

export interface Store {
  logo: string | null;
  phone: string;
  name: string;
  slug: string;
  state: string;
  city: string;
  address: string;
  industry: string;
  email: string;
  status: StoreStatus;
}

export interface StoreWithUser extends Store {
  user: User;
}

export interface StoreMetadata {
  live_products: number;
  monthly_orders: number;
  pending_payout: number;
}

/* ── Cart ─────────────────────────────────────────────────────── */

export interface CartItem {
  product_id: string;
  quantity: number;
}

export interface CartOut {
  product: Product;
  quantity: number;
}

/* ── Wishlist ─────────────────────────────────────────────────── */

export interface WishlistOut {
  product: Product;
  created_at: string;
}

/* ── Order ─────────────────────────────────────────────────────── */

export interface OrderMini {
  order_number: string;
  idompotent_key: string;
  status: OrderStatus;
  paid: boolean;
  paid_at: string | null;
  created_at: string;
}

export interface OrderProduct {
  product: Product;
  quantity: number;
  unit_price: string;
}

export interface OrderDetail extends OrderMini {
  delivery_address: Address;
  items: OrderProduct[];
}

/* ── Vendor Order ─────────────────────────────────────────────── */

export interface VendorOrderMini {
  vid: string;
  subtotal: string;
  status: "paid" | "unpaid";
  created_at: string;
  paid_at: string | null;
}

export interface VendorOrderDetail extends VendorOrderMini {
  items: {
    product_name: string;
    quantity: number;
    unit_price: string;
  }[];
}

export interface AdminVendorOrder extends VendorOrderMini {
  store: Store;
}

export interface AdminVendorOrderDetail extends AdminVendorOrder {
  order: OrderMini;
}

export interface AdminOrderDetail extends OrderDetail {
  vendors: AdminVendorOrder[];
  user: User;
}

/* ── Checkout ─────────────────────────────────────────────────── */

export interface CheckoutPayload {
  idompotent_key: string;
  items: CartItem[];
  delivery_address: string | AddressIn;
}
