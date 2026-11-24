using UnityEngine;

/// <summary>
/// Tracks the move budget and win/lose state of the current puzzle level.
/// </summary>
public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }

    [SerializeField] private int startingMoves = 25;

    public int MovesRemaining { get; private set; }
    public bool IsLevelComplete { get; private set; }
    public bool IsGameOver { get; private set; }

    private void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }

        Instance = this;
        MovesRemaining = startingMoves;
    }

    /// <summary>Call whenever the player makes a move.</summary>
    public void UseMove()
    {
        if (IsLevelComplete || IsGameOver) return;

        MovesRemaining--;
        if (MovesRemaining <= 0)
        {
            TriggerGameOver();
        }
    }

    /// <summary>Call after each move with the result of your own win check.</summary>
    public void CompleteLevel()
    {
        if (IsGameOver) return;

        IsLevelComplete = true;
        Debug.Log("Puzzle solved!");
    }

    private void TriggerGameOver()
    {
        IsGameOver = true;
        Debug.Log("Out of moves!");
    }
}
