export default async function Home() {
  // 1. Point this to the correct endpoint if "/" doesn't exist (e.g., "/lectures/")

  const WEATHER_BASE_URL = "http://api.weatherapi.com/v1"
  const WEATHER_API_KEY = process.env.WEATHER_API_KEY
  const response = await fetch(
    `${WEATHER_BASE_URL}/current.json?key=${WEATHER_API_KEY}&q=turkey`
  )
  const data = await response.json()


  // 2. Catch the FastAPI {detail} error so it doesn't crash React

  if (!response.ok) {
    const errorMessage = data.error?.message || data.detail || JSON.stringify(data)
    return (
      <div className="p-8 text-red-500">
        <h1>Failed to load data!</h1>
        <p>Error: {errorMessage}</p>
      </div>
    )
  }

  // 3. Map over the array to render specific string properties, not the whole object
  const { location, current } = data

  return (
    <main className="p-8">
      <h1 className="text-xl font-bold mb-4">Weather Dashboard</h1>
      <div className="p-4 border rounded shadow-sm max-w-sm">
        <h2 className="text-lg font-semibold text-gray-800">
          {location.name}, {location.country}
        </h2>
        <p className="text-gray-600 mt-2">
          <strong>Temperature:</strong> {current.temp_c}°C
        </p>
        <p className="text-gray-600">
          <strong>Condition:</strong> {current.condition.text}
        </p>
      </div>
    </main>
  )
}
