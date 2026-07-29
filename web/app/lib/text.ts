export function toTitleCase(str: string) {
    if (typeof str !== "string") {
        return str
    }

    return str
        .toLowerCase() // Normalize to lowercase first
        .replace(/\b\w/g, char => char.toUpperCase()); // Capitalize first letter of each word
}
