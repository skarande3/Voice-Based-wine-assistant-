export interface Wine {
  name: string;
  region: string;
  varietal: string;
  vintage: string;
  price: number;
  rating: number;
  description: string;
  abv: string;
  tags: string[];
}

// Google Sheets CSV export URL
const SHEET_URL =
  "https://docs.google.com/spreadsheets/d/1Bkv3Jb_8YuLUG2rWUhJhQBdaGjQCMFfwF9oJ5jrYDSA/export?format=csv";

export async function loadWineData(): Promise<Wine[]> {
  try {
    const response = await fetch(SHEET_URL);
    const csvText = await response.text();
    const wines = parseCSV(csvText);
    return wines;
  } catch (error) {
    console.error("Error loading wine data:", error);
    // Return mock data as fallback
    return getMockWines();
  }
}

function parseCSV(csvText: string): Wine[] {
  const lines = csvText.split("\n");
  const headers = lines[0].split(",").map((h) => h.trim().toLowerCase());

  const wines: Wine[] = [];

  for (let i = 1; i < lines.length; i++) {
    if (!lines[i].trim()) continue;

    const values = parseCSVLine(lines[i]);
    if (values.length < headers.length) continue;

    const wine: any = {};
    headers.forEach((header, index) => {
      wine[header] = values[index]?.trim() || "";
    });

    wines.push({
      name: wine.name || wine.wine || "",
      region: wine.region || "",
      varietal: wine.varietal || wine.variety || wine.grape || "",
      vintage: wine.vintage || wine.year || "",
      price: parseFloat(wine.price?.replace(/[$,]/g, "") || "0"),
      rating: parseFloat(wine.rating || wine.score || "0"),
      description: wine.description || wine.notes || "",
      abv: wine.abv || "",
      tags: wine.tags ? wine.tags.split(";").map((t: string) => t.trim()) : [],
    });
  }

  return wines;
}

function parseCSVLine(line: string): string[] {
  const values: string[] = [];
  let current = "";
  let inQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const char = line[i];

    if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === "," && !inQuotes) {
      values.push(current);
      current = "";
    } else {
      current += char;
    }
  }

  values.push(current);
  return values;
}

export function findWineAnswer(question: string, wines: Wine[]): string {
  const q = question.toLowerCase();

  // No question provided
  if (!q.trim()) {
    return "I'm here to help you discover wines! Try asking me about price, region, ratings, or what would make a good gift.";
  }

  // Price-based queries
  if (q.includes("under") || q.includes("less than") || q.includes("cheaper")) {
    const priceMatch = q.match(/\$?(\d+)/);
    if (priceMatch) {
      const maxPrice = parseInt(priceMatch[1]);
      const affordable = wines
        .filter((w) => w.price > 0 && w.price <= maxPrice)
        .sort((a, b) => b.rating - a.rating)
        .slice(0, 3);

      if (affordable.length === 0) {
        return `I don't have any wines under $${maxPrice} in the collection right now.`;
      }

      return `Here are the best-rated wines under $${maxPrice}: ${affordable
        .map((w) => `${w.name} from ${w.region} at $${w.price.toFixed(2)} (rated ${w.rating}/100)`)
        .join(", ")}. ${affordable[0].description || ""}`;
    }
  }

  // Most expensive
  if (q.includes("expensive") || q.includes("pricey") || q.includes("premium")) {
    const expensive = wines
      .filter((w) => w.price > 0)
      .sort((a, b) => b.price - a.price)
      .slice(0, 3);

    if (expensive.length === 0) {
      return "I don't have pricing information available right now.";
    }

    return `The most expensive bottle is ${expensive[0].name} from ${expensive[0].region} at $${expensive[0].price.toFixed(2)}. ${expensive[0].description || ""}`;
  }

  // Region-based queries
  const regions = ["burgundy", "napa", "bordeaux", "tuscany", "rioja", "champagne", "california", "france", "italy", "spain"];
  for (const region of regions) {
    if (q.includes(region)) {
      const fromRegion = wines
        .filter((w) => w.region.toLowerCase().includes(region))
        .sort((a, b) => b.rating - a.rating)
        .slice(0, 3);

      if (fromRegion.length === 0) {
        return `I don't have any wines from ${region.charAt(0).toUpperCase() + region.slice(1)} in stock right now.`;
      }

      return `From ${region.charAt(0).toUpperCase() + region.slice(1)}, I recommend ${fromRegion
        .map((w) => `${w.name} (${w.vintage}) at $${w.price.toFixed(2)}`)
        .join(", ")}. ${fromRegion[0].description || ""}`;
    }
  }

  // Rating-based queries
  if (q.includes("best") || q.includes("highest rated") || q.includes("top rated")) {
    const topRated = wines
      .filter((w) => w.rating > 0)
      .sort((a, b) => b.rating - a.rating)
      .slice(0, 3);

    if (topRated.length === 0) {
      return "I don't have rating information available right now.";
    }

    return `The best-rated wines are ${topRated
      .map((w) => `${w.name} from ${w.region} (rated ${w.rating}/100) at $${w.price.toFixed(2)}`)
      .join(", ")}. ${topRated[0].description || ""}`;
  }

  // Gift recommendations
  if (q.includes("gift") || q.includes("present") || q.includes("housewarming")) {
    const gifts = wines
      .filter((w) => w.price >= 25 && w.price <= 75 && w.rating >= 85)
      .sort((a, b) => b.rating - a.rating)
      .slice(0, 3);

    if (gifts.length === 0) {
      return "For gifts, I'd recommend wines in the $25-75 range with high ratings. Let me know your budget and I can find something perfect!";
    }

    return `For a gift, I'd recommend ${gifts
      .map((w) => `${w.name} from ${w.region} at $${w.price.toFixed(2)}`)
      .join(", ")}. ${gifts[0].description || "These are well-balanced and universally appreciated."}`;
  }

  // Varietal queries
  const varietals = ["pinot noir", "cabernet", "merlot", "chardonnay", "sauvignon blanc", "red", "white"];
  for (const varietal of varietals) {
    if (q.includes(varietal)) {
      const byVarietal = wines
        .filter((w) => w.varietal.toLowerCase().includes(varietal))
        .sort((a, b) => b.rating - a.rating)
        .slice(0, 3);

      if (byVarietal.length === 0) {
        return `I don't have any ${varietal} wines available right now.`;
      }

      return `For ${varietal}, I recommend ${byVarietal
        .map((w) => `${w.name} from ${w.region} at $${w.price.toFixed(2)}`)
        .join(", ")}. ${byVarietal[0].description || ""}`;
    }
  }

  // Default response for unrecognized queries
  return "I can help you find wines by price, region, rating, or occasion! Try asking about 'best wines under $50', 'wines from Burgundy', or 'what would make a good gift'.";
}

function getMockWines(): Wine[] {
  return [
    {
      name: "IMAGERY PINOT NOIR",
      region: "United States",
      varietal: "Pinot Noir",
      vintage: "2021",
      price: 16.99,
      rating: 88,
      description: "Delivers juicy and bold red fruit flavors with a smooth finish",
      abv: "15.9%",
      tags: ["bold"],
    },
    {
      name: "Château Margaux",
      region: "Bordeaux, France",
      varietal: "Cabernet Sauvignon Blend",
      vintage: "2015",
      price: 850.0,
      rating: 98,
      description: "An exceptional wine with deep complexity and elegance",
      abv: "13.5%",
      tags: ["premium", "elegant"],
    },
    {
      name: "Domaine de la Romanée-Conti",
      region: "Burgundy, France",
      varietal: "Pinot Noir",
      vintage: "2018",
      price: 3500.0,
      rating: 100,
      description: "The pinnacle of Burgundy Pinot Noir",
      abv: "13%",
      tags: ["premium", "legendary"],
    },
    {
      name: "Stag's Leap Artemis",
      region: "Napa Valley, California",
      varietal: "Cabernet Sauvignon",
      vintage: "2019",
      price: 48.0,
      rating: 92,
      description: "Rich and structured with notes of blackberry and cocoa",
      abv: "14.5%",
      tags: ["bold", "fruity"],
    },
    {
      name: "Cloudy Bay Sauvignon Blanc",
      region: "Marlborough, New Zealand",
      varietal: "Sauvignon Blanc",
      vintage: "2022",
      price: 28.0,
      rating: 90,
      description: "Crisp and vibrant with tropical fruit notes",
      abv: "13%",
      tags: ["crisp", "refreshing"],
    },
  ];
}
