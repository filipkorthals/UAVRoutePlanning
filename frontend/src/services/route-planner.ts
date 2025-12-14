import ApiResponse from "@/types/api-response";
import Marker from "@/types/marker";

const API_URL = "http://127.0.0.1:5001";

export const sendWaypoints = async (
  markers: Marker[],
  time: number,
  velocity: number
): Promise<ApiResponse> => {
  try {
    let response = await fetch(`${API_URL}/waypoints`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        waypoints: markers,
        time: time,
        velocity: velocity,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data as ApiResponse;
  } catch (error) {
    console.error("API request error: ", error);
    throw error;
  }
};
