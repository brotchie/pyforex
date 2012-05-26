package jforex;

import java.util.*;
import java.lang.System;
import java.lang.Thread;
import java.lang.InterruptedException;

import com.dukascopy.api.*;

import org.python.util.PythonInterpreter;
import org.python.core.*;

import java.nio.file.FileSystems;
import java.nio.file.WatchService;
import java.nio.file.WatchKey;
import java.nio.file.WatchEvent;
import java.nio.file.Path;
import java.io.IOException;
import static java.nio.file.StandardWatchEventKinds.ENTRY_MODIFY;

@Library("jython.jar")
public class Strategy implements IStrategy {
    private IEngine engine;
    private IConsole console;
    private IHistory history;
    private IContext context;
    private IIndicators indicators;
    private IUserInterface userInterface;
    private PythonInterpreter python;
    private IStrategy pythonStrategy;

    private static String pythonModulePath = "/home/ganon/JForex/Strategy.py";

    private class ModuleWatcher extends Thread {
        private Strategy strategy;
        private String modulePath;

        ModuleWatcher(String modulePath, Strategy strategy) {
            this.strategy = strategy;
            this.modulePath = modulePath;
        }

        public void run() {
            try {
                WatchService watcher = FileSystems.getDefault().newWatchService();
                Path path = FileSystems.getDefault().getPath(this.modulePath);
                WatchKey key = path.getParent().register(watcher, ENTRY_MODIFY);

                for (;;) {
                    key = watcher.take();
                    for (WatchEvent event: key.pollEvents()) {
                        if (event.kind() == ENTRY_MODIFY){
                            WatchEvent<Path> ev = (WatchEvent<Path>)event;
                            Path filename = ev.context();
                            if (filename.equals(path.getFileName())){
                                this.strategy.reloadPythonModule();
                            }
                        }
                    }
                    key.reset();
                }
            } catch (JFException e) {
            } catch (IOException e) {
                java.lang.System.console().printf(e.toString());
            } catch (InterruptedException e) {
                java.lang.System.console().printf("Watching thread stopped.");
            }
        }
    }

    private ModuleWatcher moduleWatcher;

    public void onStart(IContext context) throws JFException {
        this.engine = context.getEngine();
        this.console = context.getConsole();
        this.history = context.getHistory();
        this.context = context;
        this.indicators = context.getIndicators();
        this.userInterface = context.getUserInterface();
        this.moduleWatcher = new ModuleWatcher(pythonModulePath, this);
        this.moduleWatcher.start();

        this.python = new PythonInterpreter();
        this.python.setErr(java.lang.System.out);
        reloadPythonModule();
    }

    private void reloadPythonModule() throws JFException {
        synchronized(this.python) {
            this.python.execfile(pythonModulePath);
            PyObject pythonStrategyClass = this.python.get("Strategy");
            PyObject pythonStrategyObject = pythonStrategyClass.__call__();
            this.pythonStrategy = (IStrategy)pythonStrategyObject.__tojava__(IStrategy.class);
            this.pythonStrategy.onStart(this.context);
        }
    }

    public void onAccount(IAccount account) throws JFException {
        synchronized(this.python) {
            this.pythonStrategy.onAccount(account);
        }
    }

    public void onMessage(IMessage message) throws JFException {
        synchronized(this.python) {
            this.pythonStrategy.onMessage(message);
        }
    }

    public void onStop() throws JFException {
        this.moduleWatcher.interrupt();
        synchronized(this.python) {
            this.pythonStrategy.onStop();
        }
    }

    public void onTick(Instrument instrument, ITick tick) throws JFException {
        synchronized(this.python) {
            this.pythonStrategy.onTick(instrument, tick);
        }
    }
    
    public void onBar(Instrument instrument, Period period, IBar askBar, IBar bidBar) throws JFException {
        synchronized(this.python) {
            this.pythonStrategy.onBar(instrument, period, askBar, bidBar);
        }
    }
}
