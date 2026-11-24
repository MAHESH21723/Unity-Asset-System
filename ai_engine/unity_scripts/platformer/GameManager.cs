using UnityEngine;
using UnityEngine.SceneManagement;

/// <summary>
/// Persistent singleton that tracks score, lives and the game-over state.
/// Place one instance in your first (bootstrap) scene.
/// </summary>
public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }

    [Header("Game State")]
    [SerializeField] private int startingLives = 3;

    public int CurrentScore { get; private set; }
    public int PlayerLives { get; private set; }
    public bool IsGameOver { get; private set; }

    private void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }

        Instance = this;
        DontDestroyOnLoad(gameObject);
        PlayerLives = startingLives;
    }

    public void AddScore(int amount)
    {
        CurrentScore += amount;
        Debug.Log($"Score: {CurrentScore}");
    }

    public void TakeDamage(int damage)
    {
        if (IsGameOver) return;

        PlayerLives = Mathf.Max(0, PlayerLives - damage);
        if (PlayerLives == 0)
        {
            TriggerGameOver();
        }
    }

    private void TriggerGameOver()
    {
        IsGameOver = true;
        Debug.Log("Game Over!");
    }

    public void RestartGame()
    {
        CurrentScore = 0;
        PlayerLives = startingLives;
        IsGameOver = false;
        SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
    }
}
