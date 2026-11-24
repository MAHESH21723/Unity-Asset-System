using UnityEngine;

/// <summary>
/// Minimal persistent game-state singleton. Extend it with your own states.
/// </summary>
public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }

    public bool IsGameActive { get; private set; }

    private void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }

        Instance = this;
        DontDestroyOnLoad(gameObject);
    }

    public void StartGame()
    {
        IsGameActive = true;
        Debug.Log("Game started.");
    }

    public void EndGame()
    {
        IsGameActive = false;
        Debug.Log("Game finished.");
    }
}
