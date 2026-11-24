using UnityEngine;

/// <summary>
/// Side-scrolling 2D character controller: horizontal movement plus a
/// ground-checked jump. Attach to the player together with a Rigidbody2D and
/// a Collider2D, then assign a child "GroundCheck" transform at the feet.
/// </summary>
[RequireComponent(typeof(Rigidbody2D))]
[RequireComponent(typeof(Collider2D))]
public class PlayerController : MonoBehaviour
{
    [Header("Movement Settings")]
    [SerializeField] private float moveSpeed = 8f;
    [SerializeField] private float jumpForce = 12f;

    [Header("Ground Check")]
    [SerializeField] private Transform groundCheckPoint;
    [SerializeField] private float groundCheckRadius = 0.2f;
    [SerializeField] private LayerMask groundLayer;

    private Rigidbody2D rb;
    private float horizontalInput;
    private bool isGrounded;
    private bool jumpRequested;

    // Unity 6 renamed Rigidbody2D.velocity to linearVelocity.
    private Vector2 Velocity
    {
#if UNITY_6000_0_OR_NEWER
        get => rb.linearVelocity;
        set => rb.linearVelocity = value;
#else
        get => rb.velocity;
        set => rb.velocity = value;
#endif
    }

    private void Awake()
    {
        rb = GetComponent<Rigidbody2D>();
    }

    private void Update()
    {
        // Uses the legacy Input Manager axes ("Horizontal" / "Jump").
        horizontalInput = Input.GetAxisRaw("Horizontal");

        isGrounded = groundCheckPoint != null &&
                     Physics2D.OverlapCircle(groundCheckPoint.position, groundCheckRadius, groundLayer) != null;

        if (Input.GetButtonDown("Jump") && isGrounded)
        {
            jumpRequested = true;
        }
    }

    private void FixedUpdate()
    {
        // Physics changes belong in FixedUpdate.
        Velocity = new Vector2(horizontalInput * moveSpeed, Velocity.y);

        if (jumpRequested)
        {
            Velocity = new Vector2(Velocity.x, jumpForce);
            jumpRequested = false;
        }
    }

    private void OnDrawGizmosSelected()
    {
        if (groundCheckPoint == null) return;
        Gizmos.color = Color.yellow;
        Gizmos.DrawWireSphere(groundCheckPoint.position, groundCheckRadius);
    }
}
