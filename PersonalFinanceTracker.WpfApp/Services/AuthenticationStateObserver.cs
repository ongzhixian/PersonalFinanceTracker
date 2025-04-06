namespace PersonalFinanceTracker.WpfApp.Services;

class AuthenticationStateObserver : IObserver<AuthenticationState>
{
    private IDisposable unsubscriber;
    private bool first = true;
    private AuthenticationState last;

    public virtual void Subscribe(IObservable<AuthenticationState> provider)
    {
        unsubscriber = provider.Subscribe(this);
    }

    public virtual void Unsubscribe()
    {
        unsubscriber.Dispose();
    }

    public void OnCompleted()
    {
        throw new NotImplementedException();
    }

    public void OnError(Exception error)
    {
        throw new NotImplementedException();
    }

    public void OnNext(AuthenticationState value)
    {
        throw new NotImplementedException();
    }
}

class AuthenticationStateProvider : IObservable<AuthenticationState>
{
    IList<IObserver<AuthenticationState>> observers;

    public AuthenticationStateProvider()
    {
        observers = [];
    }



    private class Unsubscriber : IDisposable
    {
        private IList<IObserver<AuthenticationState>> _observers;
        private IObserver<AuthenticationState> _observer;

        public Unsubscriber(IList<IObserver<AuthenticationState>> observers, IObserver<AuthenticationState> observer)
        {
            this._observers = observers;
            this._observer = observer;
        }

        public void Dispose()
        {
            if (!(_observer == null)) _observers.Remove(_observer);
        }
    }

    public IDisposable Subscribe(IObserver<AuthenticationState> observer)
    {
        if (!observers.Contains(observer))
            observers.Add(observer);

        return new Unsubscriber(observers, observer);
    }

}

public record struct AuthenticationState
{
    public bool IsAuthenticated { get; set; }
}
