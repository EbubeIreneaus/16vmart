import type {
  AttributeKey,
  Category,
  Page,
  Product,
  Role,
  Store,
} from "~/types/api";

const images = [
  "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=80",
  "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80",
  "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80",
  "https://images.unsplash.com/photo-1503602642458-232111445657?auto=format&fit=crop&w=900&q=80",
];

const electronics: AttributeKey[] = [
  { id: 11, name: "Brand", required: true, form_type: "text", options: null },
  {
    id: 12,
    name: "Warranty",
    required: true,
    form_type: "select",
    options: ["No warranty", "6 months", "1 year", "2 years"],
  },
];
const phones: AttributeKey[] = [
  {
    id: 21,
    name: "Storage",
    required: true,
    form_type: "select",
    options: ["64GB", "128GB", "256GB", "512GB"],
  },
  {
    id: 22,
    name: "Colour",
    required: true,
    form_type: "multiple",
    options: ["Black", "Blue", "Gold", "Silver"],
  },
];

export const categories = ref<Category[]>([
  {
    id: 1,
    name: "Electronics",
    slug: "electronics",
    attributes: electronics,
    sub_categories: [
      {
        id: 2,
        name: "Mobile Phones",
        slug: "mobile-phones",
        attributes: phones,
        sub_categories: [],
      },
      {
        id: 3,
        name: "Audio",
        slug: "audio",
        attributes: [],
        sub_categories: [],
      },
    ],
  },
  {
    id: 4,
    name: "Fashion",
    slug: "fashion",
    attributes: [
      {
        id: 41,
        name: "Material",
        required: true,
        form_type: "text",
        options: null,
      },
    ],
    sub_categories: [
      {
        id: 5,
        name: "Shoes",
        slug: "shoes",
        attributes: [
          {
            id: 51,
            name: "Size",
            required: true,
            form_type: "number",
            options: null,
          },
        ],
        sub_categories: [],
      },
      {
        id: 6,
        name: "Clothing",
        slug: "clothing",
        attributes: [],
        sub_categories: [],
      },
    ],
  },
  {
    id: 7,
    name: "Home & Living",
    slug: "home-living",
    attributes: [],
    sub_categories: [
      {
        id: 8,
        name: "Furniture",
        slug: "furniture",
        attributes: [],
        sub_categories: [],
      },
      {
        id: 9,
        name: "Kitchen",
        slug: "kitchen",
        attributes: [],
        sub_categories: [],
      },
    ],
  },
]);

const coreProducts: Product[] = [
  {
    name: "Apex wireless headphones",
    price: "18500.00",
    description: "Immersive sound with all-day comfort.",
    condition: "brand new",
    available: true,
    slug: "apex-wireless-headphones",
    images: [{ src: images[1], alt: "Wireless headphones" }],
    category: { name: "Audio", slug: "audio" },
  },
  {
    name: "Classic chronograph watch",
    price: "32000.00",
    description: "A polished everyday statement piece.",
    condition: "brand new",
    available: true,
    slug: "classic-chronograph-watch",
    images: [{ src: images[0], alt: "Chronograph watch" }],
    category: { name: "Fashion", slug: "fashion" },
  },
  {
    name: "Nimbus running shoes",
    price: "24500.00",
    description: "Lightweight trainers for daily miles.",
    condition: "brand new",
    available: true,
    slug: "nimbus-running-shoes",
    images: [{ src: images[2], alt: "Running shoes" }],
    category: { name: "Shoes", slug: "shoes" },
  },
  {
    name: "Luna lounge chair",
    price: "89500.00",
    description: "Contemporary comfort for your space.",
    condition: "brand new",
    available: true,
    slug: "luna-lounge-chair",
    images: [{ src: images[3], alt: "Lounge chair" }],
    category: { name: "Furniture", slug: "furniture" },
  },
];

// Deliberately paginated mock inventory: each item retains the exact MiniProductResponse shape.
const products: Product[] = Array.from({ length: 6 }, (_, index) =>
  coreProducts.map((product, itemIndex) => ({
    ...product,
    name: index === 0 ? product.name : `${product.name} · Edition ${index + 1}`,
    slug: index === 0 ? product.slug : `${product.slug}-${index + 1}`,
    price: String(Number(product.price) + index * 2500 + itemIndex * 500),
  })),
).flat();

export const mockProducts = ref<Product[]>(products);
export const useMockRole = () =>
  useState<Role>("mock-role", () => "superadmin");
export const useMockStores = () =>
  useState<Store[]>("mock-stores", () => ([{
    logo: null,
    phone: "+234 801 234 5678",
    name: "Northstar Goods",
    slug: "northstar-goods",
    state: "Lagos",
    city: "Lekki",
    address: "14 Admiralty Way",
    industry: "Lifestyle & electronics",
    email: "hello@northstar.example",
    status: "active",
  }, {
    logo: null,
    phone: "+234 803 987 6543",
    name: "Luma Home Studio",
    slug: "luma-home-studio",
    state: "Lagos",
    city: "Ikeja",
    address: "24 Opebi Road",
    industry: "Home & living",
    email: "hello@lumahome.example",
    status: "under_review",
  }]));

export const useMockStore = (slug = "northstar-goods") => {
  const stores = useMockStores()
  return computed(() => stores.value.find((store) => store.slug === slug) || stores.value[0])
}
  
export const pageOf = <T>(items: T[], page = 1, size = 50): Page<T> => ({
  items: items.slice((page - 1) * size, page * size),
  total: items.length,
  page,
  size,
  pages: Math.max(1, Math.ceil(items.length / size)),
});

export const formatNaira = (amount: string | number) =>
  new Intl.NumberFormat("en-NG", {
    style: "currency",
    currency: "NGN",
    maximumFractionDigits: 0,
  }).format(Number(amount));

  export const formatUSD = (amount: string | number) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(Number(amount));

export const inheritedAttributes = (subcategoryId: number) => {
  const parent = categories.value.find((category) =>
    category.sub_categories.some((sub) => sub.id === subcategoryId),
  );
  const child = parent?.sub_categories.find((sub) => sub.id === subcategoryId);
  return [...(parent?.attributes || []), ...(child?.attributes || [])];
};
