using System;
using UnityEngine;

/// <summary>
/// Reusable hit-point component for the player, enemies and destructibles.
/// </summary>
public class Health : MonoBehaviour
{
    [SerializeField] private int maxHealth = 100;

    public int Current { get; private set; }
    public bool IsDead => Current <= 0;

    /// <summary>Raised once when health reaches zero.</summary>
    public event Action<Health> Died;

    private void Awake()
    {
        Current = maxHealth;
    }

    public void TakeDamage(int amount)
    {
        if (IsDead || amount <= 0) return;

        Current = Mathf.Max(0, Current - amount);
        if (IsDead)
        {
            Died?.Invoke(this);
            Destroy(gameObject);
        }
    }
}
