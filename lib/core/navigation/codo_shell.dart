import 'package:flutter/material.dart';

import '../../features/ai/codo_ai_screen.dart';
import '../../features/home/home_screen.dart';
import '../../features/procedures/procedures_screen.dart';
import '../../features/search/search_screen.dart';
import '../../features/space/user_space_screen.dart';

class CodoShell extends StatefulWidget {
  const CodoShell({super.key});

  @override
  State<CodoShell> createState() => _CodoShellState();
}

class _CodoShellState extends State<CodoShell> {
  var index = 0;

  late final pages = <Widget>[
    HomeScreen(onNavigate: _goTo),
    const SearchScreen(),
    const CodoAiScreen(),
    const ProceduresScreen(),
    const UserSpaceScreen(),
  ];

  void _goTo(int nextIndex) => setState(() => index = nextIndex);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(child: IndexedStack(index: index, children: pages)),
      bottomNavigationBar: NavigationBar(
        selectedIndex: index,
        onDestinationSelected: _goTo,
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Accueil'),
          NavigationDestination(icon: Icon(Icons.search_rounded), label: 'Recherche'),
          NavigationDestination(icon: Icon(Icons.chat_bubble_outline_rounded), label: 'CODO'),
          NavigationDestination(icon: Icon(Icons.route_outlined), label: 'Procédures'),
          NavigationDestination(icon: Icon(Icons.person_outline_rounded), label: 'Espace'),
        ],
      ),
    );
  }
}
