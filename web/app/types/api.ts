export type FormType =
  | "text"
  | "select"
  | "multiple"
  | "radio"
  | "date"
  | "boolean"
  | "number";
export type Role = "user" | "seller" | "admin" | "superadmin";
export type StoreStatus =
  | "active"
  | "suspended"
  | "terminated"
  | "hibernating"
  | "under_review"
  | "deactivated";

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}
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
  sub_categories: Category[];
  attributes?: AttributeKey[];
}
export interface Image {
  src: string;
  alt: string | null;
}
export interface Product {
  name: string;
  price: string;
  description: string;
  condition: "brand new" | "used";
  available: boolean;
  slug: string;
  images: Image[];
  category?: { name: string; slug: string };
  attributes?: {
    name: string;
    type: string;
    value: string | number | boolean | string[];
  }[];
}
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
