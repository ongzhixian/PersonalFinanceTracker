using System.ComponentModel;
using System.Runtime.CompilerServices;

namespace PersonalFinanceTracker.WpfApp.Services;

public interface IAuthenticationService 
{
    event PropertyChangedEventHandler? AuthenticatedStateChanged;
    Task AuthenticateCredentialsAsync(string username, string password);

    bool IsUserAuthenticated { get; }
    
    void OnAuthenticatedStateChanged([CallerMemberName] string propertyName = null);
}

public class AuthenticationService : IAuthenticationService
{
    private string jwt = string.Empty;

    public AuthenticationService()
    {
    }

    public async Task AuthenticateCredentialsAsync(string username, string password)
    {
        await Task.Delay(1000);
        //Thread.Sleep(1300); // Simulate DB

        if (username.Equals("zhixian", StringComparison.InvariantCultureIgnoreCase) 
            && password.Equals("pass", StringComparison.InvariantCultureIgnoreCase))
        {
            jwt = "SOME-USERNAME-PASSWORD-JWT";

            OnAuthenticatedStateChanged("AA");
            //// Create a RoutedEventArgs instance.
            //RoutedEventArgs routedEventArgs = new(routedEvent: AuthenticatedStateChangedEvent);

            //// Raise the event, which will bubble up through the element tree.
            //RaiseEvent(routedEventArgs);
        }

    }

    public bool IsUserAuthenticated
    {
        get {

            return !string.IsNullOrWhiteSpace(jwt);
        }
    }

    public virtual void OnAuthenticatedStateChanged([CallerMemberName] string propertyName = null)
    {
        AuthenticatedStateChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }

    public void RaiseAuthenticatedStateChangedEvent()
    {
        // Create a RoutedEventArgs instance.
        //RoutedEventArgs routedEventArgs = new(routedEvent: AuthenticatedStateChangedEvent);

        //// Raise the event, which will bubble up through the element tree.
        //RaiseEvent(routedEventArgs);
        
    }

    //public static readonly RoutedEvent AuthenticatedStateChangedEvent = EventManager.RegisterRoutedEvent(
    //        name: "AuthenticatedStateChangedEvent",
    //        routingStrategy: RoutingStrategy.Bubble,
    //        handlerType: typeof(RoutedEventHandler),
    //        ownerType: typeof(UserControl));

    public event PropertyChangedEventHandler? AuthenticatedStateChanged;

    //public event EventHandler AuthenticatedStateChangedEvent;
    
}
