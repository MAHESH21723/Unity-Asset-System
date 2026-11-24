using UnityEngine;

/// <summary>
/// Builds a centered width x height board of tile prefabs and lets other
/// systems look tiles up by grid coordinate.
/// </summary>
public class GridManager : MonoBehaviour
{
    public static GridManager Instance { get; private set; }

    [Header("Grid Config")]
    [SerializeField] private int width = 6;
    [SerializeField] private int height = 6;
    [SerializeField] private GameObject tilePrefab;
    [SerializeField] private float spacing = 1.1f;

    private GameObject[,] grid;

    private void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }

        Instance = this;
    }

    private void Start()
    {
        GenerateGrid();
    }

    private void GenerateGrid()
    {
        if (tilePrefab == null)
        {
            Debug.LogError("GridManager: assign a tile prefab in the Inspector.", this);
            return;
        }

        grid = new GameObject[width, height];
        Vector3 offset = new Vector3((width - 1) * spacing / 2f, (height - 1) * spacing / 2f, 0f);
        Vector3 startPos = transform.position - offset;

        for (int x = 0; x < width; x++)
        {
            for (int y = 0; y < height; y++)
            {
                Vector3 position = startPos + new Vector3(x * spacing, y * spacing, 0f);
                GameObject tile = Instantiate(tilePrefab, position, Quaternion.identity, transform);
                tile.name = $"Tile_{x}_{y}";
                grid[x, y] = tile;
            }
        }
    }

    public GameObject GetTileAt(int x, int y)
    {
        if (grid == null) return null;
        if (x < 0 || x >= width || y < 0 || y >= height) return null;
        return grid[x, y];
    }
}
